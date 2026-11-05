"""Provisionamento explícito da instalação no host; nunca executado no startup."""
import os
from pathlib import Path
import re
from urllib.parse import quote

from dotenv import load_dotenv, set_key
from minio import Minio
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3 import PoolManager, Timeout


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
        key = next(iter(body))
        expected_name = body[key].get("name")
        existing = current.get(key, current)
        if expected_name and existing.get("name") != expected_name:
            raise RuntimeError(f"Recurso existente incompatível em {path}")
        return current

    def identity(self, name, role, catalog, env_path):
        path = "/api/management/v1/principals"
        prefix = "POLARIS" if role == "writer" else "POLARIS_READER"
        principal = self.call("GET", path + "/" + name, missing=True)
        if principal is None:
            result = self.call("POST", path, {
                "principal": {"name": name}, "credentialRotationRequired": False,
            })
            for suffix, field in (("CLIENT_ID", "clientId"), ("CLIENT_SECRET", "clientSecret")):
                key = f"{prefix}_{suffix}"
                value = result["credentials"][field]
                set_key(env_path, key, value)
                os.environ[key] = value
        # Existente: conferir o .env sem rotacionar nem depender de arquivos intermediários.
        response = self.session.post(
            self.base + "/api/catalog/v1/oauth/tokens",
            data={"grant_type": "client_credentials", "scope": "PRINCIPAL_ROLE:ALL",
                  "client_id": required(f"{prefix}_CLIENT_ID"),
                  "client_secret": required(f"{prefix}_CLIENT_SECRET")}, timeout=30)
        if not response.ok:
            raise RuntimeError(f"Credenciais {prefix} do .env recusadas: HTTP {response.status_code}")
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
            self.call("PUT", path, {"grant": grant})


def main():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.is_file():
        raise RuntimeError("Configure .env antes de provisionar")
    load_dotenv(env_path)
    endpoint = required("S3_ENDPOINT")
    client = Minio(endpoint, access_key=required("RUSTFS_ACCESS_KEY"),
                   secret_key=required("RUSTFS_SECRET_KEY"),
                   secure=os.getenv("S3_USE_SSL", "false").lower() == "true",
                   region=os.getenv("S3_REGION", "us-east-1"),
                   http_client=PoolManager(timeout=Timeout(connect=5, read=30),
                                           retries=Retry(total=3, backoff_factor=1,
                                                         status_forcelist=[502, 503, 504])))
    for bucket in ("bronze", "prata", "ouro", "iceberg"):
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
    catalog = os.getenv("ICEBERG_WAREHOUSE", "prefect")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalog):
        raise RuntimeError("Nome de catálogo inválido")
    api = Polaris()
    storage = {
        "storageType": "S3", "endpoint": "http://" + os.getenv("S3_INTERNAL_ENDPOINT", "rustfs:9000"),
        "endpointInternal": "http://" + os.getenv("S3_INTERNAL_ENDPOINT", "rustfs:9000"), "pathStyleAccess": True,
        "region": os.getenv("S3_REGION", "us-east-1"),
        "allowedLocations": ["s3://iceberg/warehouse"],
    }
    if os.getenv("S3_USE_SSL", "false").lower() == "true":
        storage["endpoint"] = storage["endpointInternal"] = "https://" + os.getenv("S3_INTERNAL_ENDPOINT", "rustfs:9000")
    desired = {"name": catalog, "type": "INTERNAL", "readOnly": False,
               "properties": {"default-base-location": "s3://iceberg/warehouse"},
               "storageConfigInfo": storage}
    result = api.ensure("/api/management/v1/catalogs", catalog, {"catalog": desired})
    existing = result.get("catalog", result)
    if existing.get("storageConfigInfo", {}).get("endpoint") != storage["endpoint"]:
        raise RuntimeError("Catálogo existente diverge do endpoint esperado; não alterar automaticamente")
    api.identity("pipeline", "writer", catalog, env_path)
    api.identity("trino", "reader", catalog, env_path)
    api.grant(catalog, "writer", {"type": "catalog", "privilege": "CATALOG_MANAGE_CONTENT"})
    for namespace in ("prata_camara_deputados", "ouro_camara_deputados"):
        base = f"/api/catalog/v1/{catalog}/namespaces"
        if api.call("GET", base + "/" + namespace, missing=True) is None:
            api.call("POST", base, {"namespace": [namespace], "properties": {}})
    api.grant(catalog, "reader", {"type": "catalog", "privilege": "CATALOG_READ_PROPERTIES"})
    # Listar namespaces não concede leitura de tabelas fora da Ouro.
    api.grant(catalog, "reader", {"type": "catalog", "privilege": "NAMESPACE_LIST"})
    for privilege in ("NAMESPACE_LIST", "NAMESPACE_READ_PROPERTIES", "TABLE_LIST", "TABLE_READ_DATA", "TABLE_READ_PROPERTIES", "VIEW_LIST", "VIEW_READ_PROPERTIES"):
        api.grant(catalog, "reader", {"type": "namespace", "namespace": ["ouro_camara_deputados"], "privilege": privilege})
    print("Provisionamento concluído: buckets, catálogo, identidades e namespaces; credenciais no .env local.")


if __name__ == "__main__":
    main()
