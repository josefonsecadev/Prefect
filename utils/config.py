"""Configuração compartilhada do armazenamento S3 e catálogo Polaris."""
import os
from urllib.parse import urlparse

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Erro de configuração sem exposição de valores sensíveis."""


class Config:
    def __init__(self):
        load_dotenv()
        self.storage_format = os.getenv("PIPELINE_STORAGE_FORMAT", "iceberg").strip().lower()
        if self.storage_format not in {"iceberg", "parquet"}:
            raise ConfigError("PIPELINE_STORAGE_FORMAT deve ser iceberg ou parquet")
        self.ambiente = os.getenv("AMBIENTE", "local")
        self.s3_endpoint = self._get_required_env("S3_ENDPOINT")
        if "://" in self.s3_endpoint or "/" in self.s3_endpoint:
            raise ConfigError("S3_ENDPOINT deve conter somente host:porta")
        self.s3_access_key = self._get_required_env("S3_ACCESS_KEY")
        self.s3_secret_key = self._get_required_env("S3_SECRET_KEY")
        self.s3_region = os.getenv("S3_REGION", "us-east-1")
        self.s3_use_ssl = self._boolean("S3_USE_SSL", "false")
        self.s3_url_style = os.getenv("S3_URL_STYLE", "path")
        if self.s3_url_style not in {"path", "vhost"}:
            raise ConfigError("S3_URL_STYLE deve ser path ou vhost")
        self.duckdb_memory_limit = os.getenv("DUCKDB_MEMORY_LIMIT", "128MB")
        self.duckdb_temp_directory = os.getenv("DUCKDB_TEMP_DIRECTORY", ".prefect/duckdb-tmp")
        if self.storage_format == "parquet":
            return
        self.iceberg_catalog_endpoint = self._get_required_env("ICEBERG_CATALOG_ENDPOINT").rstrip("/")
        parsed = urlparse(self.iceberg_catalog_endpoint)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username:
            raise ConfigError("ICEBERG_CATALOG_ENDPOINT deve ser uma URL HTTP(S) sem credenciais")
        self.iceberg_warehouse = os.getenv("ICEBERG_WAREHOUSE", "prefect")
        self.iceberg_catalog_name = os.getenv("ICEBERG_CATALOG_NAME", "lakehouse")
        self.polaris_client_id = self._get_required_env("POLARIS_CLIENT_ID")
        self.polaris_client_secret = self._get_required_env("POLARIS_CLIENT_SECRET")
        self.polaris_scope = os.getenv("POLARIS_SCOPE", "PRINCIPAL_ROLE:ALL")

    @staticmethod
    def _get_required_env(variable: str) -> str:
        value = os.getenv(variable)
        if value is None or not value.strip() or value.startswith("change-me"):
            raise ConfigError(f"Variável obrigatória não configurada: {variable}")
        return value.strip()

    @staticmethod
    def _boolean(variable: str, default: str) -> bool:
        value = os.getenv(variable, default).strip().lower()
        if value not in {"true", "false"}:
            raise ConfigError(f"{variable} deve ser true ou false")
        return value == "true"
