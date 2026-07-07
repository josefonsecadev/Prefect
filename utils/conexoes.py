from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

import duckdb
from minio import Minio

try:
    from .config import Config
except ImportError:  # pragma: no cover
    from config import Config

class Conexoes(Config):
    """
    Classe para padronizar a configuração de acesso as configuracoes
    """

    def __init__(self):
        super().__init__()
        self.duckdb_conn = self._duckdb()
    
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