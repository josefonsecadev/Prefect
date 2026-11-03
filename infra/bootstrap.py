"""Provisiona catálogo e identidades do ambiente novo sem imprimir segredos."""
import json
import os
from pathlib import Path
import re
from urllib.parse import quote

from dotenv import load_dotenv
from minio import Minio
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def required(name):
    value = os.environ.get(name, "")
    if not value or value.startswith("change-me"):
        raise RuntimeError(f"Configure {name} antes de inicializar")
    return value


class Polaris:
    def __init__(self):
        self.base = required("ICEBERG_CATALOG_ENDPOINT").removesuffix("/api/catalog")
        self.session = requests.Session()
        self.session.mount("http://", HTTPAdapter(max_retries=Retry(
            total=3, backoff_factor=1, status_forcelist=[502, 503, 504],
            allowed_methods={"GET"},
        )))
        self.session.headers["Polaris-Realm"] = "POLARIS"
        response = self.session.post(
            self.base + "/api/catalog/v1/oauth/tokens",
            data={"grant_type": "client_credentials", "scope": "PRINCIPAL_ROLE:ALL",
                  "client_id": required("POLARIS_ROOT_CLIENT_ID"),
                  "client_secret": required("POLARIS_ROOT_CLIENT_SECRET")}, timeout=30,
        )
        if not response.ok:
            raise RuntimeError(f"OAuth2 bootstrap recusado: HTTP {response.status_code}")
        self.session.headers["Authorization"] = "Bearer " + response.json()["access_token"]

    def call(self, method, path, body=None, missing=False):
        response = self.session.request(method, self.base + path, json=body, timeout=30)
        if missing and response.status_code == 404:
            return None
        if not response.ok:
            # Não incluir corpo/headers: respostas podem conter credenciais.
            raise RuntimeError(f"Polaris {method} {path}: HTTP {response.status_code}")
        return response.json() if response.content else {}

    def ensure(self, collection, name, body):
        path = collection + "/" + quote(name, safe="")
        current = self.call("GET", path, missing=True)
        if current is None:
            return self.call("POST", collection, body)
        return current

    def identity(self, name, role, catalog, runtime):
        path = "/api/management/v1/principals"
        credentials_path = runtime / f"{role}.env"
        principal = self.call("GET", path + "/" + name, missing=True)
        if principal is None:
            result = self.call("POST", path, {
                "principal": {"name": name}, "credentialRotationRequired": False,
            })
            creds = result["credentials"]
            values = {"POLARIS_CLIENT_ID": creds["clientId"],
                      "POLARIS_CLIENT_SECRET": creds["clientSecret"]}
            # Geradas pelo servidor, usadas também pelo shell do Trino.
            if any(not re.fullmatch(r"[A-Za-z0-9._~+/=-]+", v) for v in values.values()):
                raise RuntimeError("Formato de credencial não suportado para arquivo env")
            descriptor = os.open(credentials_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write("".join(f"{key}={value}\n" for key, value in values.items()))
        elif not credentials_path.exists():
            raise RuntimeError(f"Principal {name} existe, mas seu arquivo de credenciais foi perdido; recuperar/rotacionar explicitamente")
        management = "/api/management/v1"
        self.ensure(management + "/principal-roles", role, {"principalRole": {"name": role}})
        self.ensure(f"{management}/catalogs/{catalog}/catalog-roles", role,
                    {"catalogRole": {"name": role}})
        assigned = self.call("GET", f"{management}/principals/{name}/principal-roles")["roles"]
        if role not in [item["name"] for item in assigned]:
            self.call("PUT", f"{management}/principals/{name}/principal-roles",
                      {"principalRole": {"name": role}})
        assigned = self.call("GET", f"{management}/principal-roles/{role}/catalog-roles/{catalog}")["roles"]
        if role not in [item["name"] for item in assigned]:
            self.call("PUT", f"{management}/principal-roles/{role}/catalog-roles/{catalog}",
                      {"catalogRole": {"name": role}})

    def grant(self, catalog, role, grant):
        path = f"/api/management/v1/catalogs/{catalog}/catalog-roles/{role}/grants"
        existing = self.call("GET", path)["grants"]
        if grant not in existing:
            self.call("PUT", path, grant)


def main():
    load_dotenv()
    runtime = Path(os.getenv("POLARIS_RUNTIME_DIR", "/runtime"))
    runtime.mkdir(parents=True, exist_ok=True)
    endpoint = required("S3_ENDPOINT")
    client = Minio(endpoint, access_key=required("RUSTFS_ACCESS_KEY"),
                   secret_key=required("RUSTFS_SECRET_KEY"),
                   secure=os.getenv("S3_USE_SSL", "false").lower() == "true",
                   region=os.getenv("S3_REGION", "us-east-1"))
    for bucket in ("bronze", "prata", "ouro", "iceberg"):
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
    catalog = os.getenv("ICEBERG_WAREHOUSE", "prefect")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalog):
        raise RuntimeError("Nome de catálogo inválido")
    api = Polaris()
    storage = {
        "storageType": "S3", "endpoint": "http://" + endpoint,
        "endpointInternal": "http://" + endpoint, "pathStyleAccess": True,
        "region": os.getenv("S3_REGION", "us-east-1"),
        "allowedLocations": ["s3://iceberg/warehouse"],
    }
    if os.getenv("S3_USE_SSL", "false").lower() == "true":
        storage["endpoint"] = storage["endpointInternal"] = "https://" + endpoint
    desired = {"name": catalog, "type": "INTERNAL", "readOnly": False,
               "properties": {"default-base-location": "s3://iceberg/warehouse"},
               "storageConfigInfo": storage}
    result = api.ensure("/api/management/v1/catalogs", catalog, {"catalog": desired})
    existing = result.get("catalog", result)
    if existing.get("storageConfigInfo", {}).get("endpoint") != storage["endpoint"]:
        raise RuntimeError("Catálogo existente diverge do endpoint esperado; não alterar automaticamente")
    api.identity("pipeline", "writer", catalog, runtime)
    api.identity("trino", "reader", catalog, runtime)
    api.grant(catalog, "writer", {"type": "catalog", "privilege": "CATALOG_MANAGE_CONTENT"})
    for namespace in ("prata_camara_deputados", "ouro_camara_deputados"):
        base = f"/api/catalog/v1/{catalog}/namespaces"
        if api.call("GET", base + "/" + namespace, missing=True) is None:
            api.call("POST", base, {"namespace": [namespace], "properties": {}})
    for privilege in ("NAMESPACE_LIST", "TABLE_LIST", "TABLE_READ_DATA", "TABLE_READ_PROPERTIES", "VIEW_LIST", "VIEW_READ_PROPERTIES"):
        api.grant(catalog, "reader", {"type": "namespace", "namespace": ["ouro_camara_deputados"], "privilege": privilege})
    print("Bootstrap concluído: buckets, catálogo, identidades e namespaces; segredos em arquivos locais protegidos.")


if __name__ == "__main__":
    main()
