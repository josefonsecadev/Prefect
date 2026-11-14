from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import re
from typing import Iterator

import duckdb
from minio import Minio
import requests
from urllib3 import PoolManager, Timeout
from urllib3.util.retry import Retry

from .config import Config, ConfigError


class Conexoes(Config):
    """Clientes S3 e Iceberg REST compartilhando configuração explícita."""

    def __init__(self):
        super().__init__()
        self.duckdb_conn = self._duckdb()
        self._iceberg_attached = False

    @contextmanager
    def _s3(self) -> Iterator[Minio]:
        client = Minio(
            endpoint=self.s3_endpoint,
            access_key=self.s3_access_key,
            secret_key=self.s3_secret_key,
            secure=self.s3_use_ssl,
            region=self.s3_region,
            http_client=PoolManager(timeout=Timeout(connect=5, read=30),
                                    retries=Retry(total=3, backoff_factor=1,
                                                  status_forcelist=[502, 503, 504])),
        )
        yield client

    def _duckdb(self, database: str = ":memory:") -> duckdb.DuckDBPyConnection:
        con = duckdb.connect(database=database)
        con.execute("SET memory_limit = ?", [self.duckdb_memory_limit])
        con.execute("SET threads = 1")
        Path(self.duckdb_temp_directory).mkdir(parents=True, exist_ok=True)
        con.execute("SET temp_directory = ?", [self.duckdb_temp_directory])
        con.execute("SET preserve_insertion_order = false")
        con.execute("SET http_timeout = 120000")  # 120s em ms
        con.execute("SET http_retries = 5")        # 5 tentativas
        extensions = ("httpfs", "iceberg") if self.storage_format == "iceberg" else ("httpfs",)
        for extension in extensions:
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

    def _attach_iceberg_catalog(self) -> str:
        if self.storage_format != "iceberg":
            raise ConfigError("Operação exclusiva de catálogo exige PIPELINE_STORAGE_FORMAT=iceberg")
        if not self._iceberg_attached:
            catalog = self._sql_identifier(self.iceberg_catalog_name)
            endpoint = self._sql_literal(self.iceberg_catalog_endpoint)
            warehouse = self._sql_literal(self.iceberg_warehouse)
            self.duckdb_conn.execute(
                f"ATTACH {warehouse} AS {catalog} "
                f"(TYPE iceberg, ENDPOINT {endpoint}, "
                "AUTHORIZATION_TYPE 'none', "
                "ACCESS_DELEGATION_MODE 'none', SUPPORT_NESTED_NAMESPACES true)"
            )
            self._iceberg_attached = True
        return self.iceberg_catalog_name
