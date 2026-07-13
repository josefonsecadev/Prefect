from __future__ import annotations

from contextlib import contextmanager
import re
from typing import Iterator, Optional

import duckdb
from minio import Minio

try:
    from .config import Config, ConfigError
except ImportError:  # pragma: no cover
    from config import Config, ConfigError

class Conexoes(Config):
    """
    Classe para padronizar a configuração de acesso as configuracoes
    """

    def __init__(self):
        super().__init__()
        self.duckdb_conn = self._duckdb()
        self._iceberg_attached = False
    
    @contextmanager
    def _minio(self) -> Iterator[Minio]:
        """
        Inicia conexção com o Minio
        """
        
        minio_client = Minio(
            endpoint=self.minio_endpoint,
            access_key=self.minio_login,
            secret_key=self.minio_password,
            secure=False
        )
        
        yield minio_client

    def _duckdb(self,
                database: Optional[str] = ":memory:",
                minio_secure: Optional[bool] = False,
                minio_region: Optional[str] = "us-east-1",
                url_style: Optional[str] = "path"
                ) -> duckdb.DuckDBPyConnection:

        
        """
        Cria uma conexão DuckDB já configurada com as extensões
        'httpfs' e 'iceberg', e com acesso a um bucket S3/MinIO.
        
        Args:
            database: caminho do arquivo .duckdb ou ':memory:' (padrão)
            minio_secure: True se o MinIO estiver atrás de HTTPS
            minio_region: região S3 (MinIO geralmente aceita qualquer valor)
            url_style: "path" (padrão MinIO) ou "vhost"
        Returns:
            (duckdb.DuckDBPyConnection): conexão DuckDB configurada
        """
    
        con = duckdb.connect(database=database)

        con.execute("INSTALL httpfs;")
        con.execute("LOAD httpfs;")
        con.execute("INSTALL iceberg;")
        con.execute("LOAD iceberg;")


        con.execute(f"SET s3_endpoint='{self.minio_endpoint}';")
        con.execute(f"SET s3_access_key_id='{self.minio_login}';")
        con.execute(f"SET s3_secret_access_key='{self.minio_password}';")
        con.execute(f"SET s3_region='{minio_region}';")
        con.execute(f"SET s3_url_style='{url_style}';")
        con.execute(f"SET s3_use_ssl={'true' if minio_secure else 'false'};")

        return con

    @staticmethod
    def _sql_identifier(value: str) -> str:
        """Valida identificadores usados em comandos estruturais."""

        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError(f"Identificador SQL inválido: {value!r}")
        return f'"{value}"'

    @staticmethod
    def _sql_literal(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def _attach_iceberg_catalog(self) -> str:
        """Anexa uma vez o catálogo REST usado para leituras e commits Iceberg."""

        if self._iceberg_attached:
            return self.iceberg_catalog_name
        if not self.iceberg_catalog_endpoint:
            raise ConfigError(
                "Variável de ambiente obrigatória não configurada: "
                "ICEBERG_CATALOG_ENDPOINT"
            )

        catalog = self._sql_identifier(self.iceberg_catalog_name)
        endpoint = self._sql_literal(self.iceberg_catalog_endpoint.rstrip("/"))
        warehouse = self._sql_literal(self.iceberg_warehouse)

        if self.iceberg_token:
            token = self._sql_literal(self.iceberg_token)
            self.duckdb_conn.execute(
                f"CREATE OR REPLACE TEMP SECRET iceberg_catalog_secret "
                f"(TYPE iceberg, TOKEN {token})"
            )
            authentication = "SECRET iceberg_catalog_secret"
        else:
            authentication = (
                "AUTHORIZATION_TYPE 'none', ACCESS_DELEGATION_MODE 'none'"
            )

        self.duckdb_conn.execute(
            f"ATTACH {warehouse} AS {catalog} "
            f"(TYPE iceberg, ENDPOINT {endpoint}, {authentication}, "
            f"SUPPORT_NESTED_NAMESPACES true)"
        )
        self._iceberg_attached = True
        return self.iceberg_catalog_name
