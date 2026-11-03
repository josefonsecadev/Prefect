from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import re
import time
from typing import Iterator

import duckdb
from minio import Minio
import requests

from .config import Config, ConfigError


class Conexoes(Config):
    """Clientes S3 e Iceberg REST compartilhando configuração explícita."""

    def __init__(self):
        super().__init__()
        self.duckdb_conn = self._duckdb()
        self._iceberg_attached = False
        self._token_expires_at = 0.0

    @contextmanager
    def _s3(self) -> Iterator[Minio]:
        client = Minio(
            endpoint=self.s3_endpoint,
            access_key=self.s3_access_key,
            secret_key=self.s3_secret_key,
            secure=self.s3_use_ssl,
            region=self.s3_region,
        )
        yield client

    def _duckdb(self, database: str = ":memory:") -> duckdb.DuckDBPyConnection:
        con = duckdb.connect(database=database)
        con.execute("SET memory_limit = ?", [self.duckdb_memory_limit])
        con.execute("SET threads = 1")
        Path(self.duckdb_temp_directory).mkdir(parents=True, exist_ok=True)
        con.execute("SET temp_directory = ?", [self.duckdb_temp_directory])
        con.execute("SET preserve_insertion_order = false")
        for extension in ("httpfs", "iceberg"):
            con.execute(f"INSTALL {extension}")
            con.execute(f"LOAD {extension}")
        # Literais escapados; nunca registrar comandos contendo credenciais.
        settings = {
            "s3_endpoint": self.s3_endpoint,
            "s3_access_key_id": self.s3_access_key,
            "s3_secret_access_key": self.s3_secret_key,
            "s3_region": self.s3_region,
            "s3_url_style": self.s3_url_style,
        }
        for key, value in settings.items():
            con.execute(f"SET {key} = {self._sql_literal(value)}")
        con.execute(f"SET s3_use_ssl = {'true' if self.s3_use_ssl else 'false'}")
        return con

    @staticmethod
    def _sql_identifier(value: str) -> str:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError(f"Identificador SQL inválido: {value!r}")
        return f'"{value}"'

    @staticmethod
    def _sql_literal(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def _refresh_catalog_token(self) -> None:
        if time.monotonic() < self._token_expires_at:
            return
        try:
            response = requests.post(
                f"{self.iceberg_catalog_endpoint}/v1/oauth/tokens",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.polaris_client_id,
                    "client_secret": self.polaris_client_secret,
                    "scope": self.polaris_scope,
                },
                timeout=(10, 30),
            )
            response.raise_for_status()
            payload = response.json()
            token = payload["access_token"]
            lifetime = int(payload.get("expires_in", 300))
            if not isinstance(token, str) or not token or lifetime <= 0:
                raise ValueError("Resposta OAuth2 inválida")
        except (requests.RequestException, ValueError, KeyError, TypeError):
            raise ConfigError("Não foi possível autenticar no catálogo Polaris") from None
        self.duckdb_conn.execute(
            "CREATE OR REPLACE TEMP SECRET iceberg_catalog_secret "
            f"(TYPE iceberg, TOKEN {self._sql_literal(token)})"
        )
        self._token_expires_at = time.monotonic() + max(1, lifetime - 60)

    def _attach_iceberg_catalog(self) -> str:
        self._refresh_catalog_token()
        if not self._iceberg_attached:
            catalog = self._sql_identifier(self.iceberg_catalog_name)
            endpoint = self._sql_literal(self.iceberg_catalog_endpoint)
            warehouse = self._sql_literal(self.iceberg_warehouse)
            self.duckdb_conn.execute(
                f"ATTACH {warehouse} AS {catalog} "
                f"(TYPE iceberg, ENDPOINT {endpoint}, SECRET iceberg_catalog_secret, "
                "ACCESS_DELEGATION_MODE 'none', SUPPORT_NESTED_NAMESPACES true)"
            )
            self._iceberg_attached = True
        return self.iceberg_catalog_name
