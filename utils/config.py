from dotenv import load_dotenv
import os


class ConfigError(RuntimeError):
  """Erro de configuração sem exposição de valores sensíveis."""


class Config:
  """
  Classe por padronizar a configuração de acesso ao MiniO
  """

  def __init__(self):
    load_dotenv()
    self.ambiente = os.getenv('AMBIENTE')
    self.minio_endpoint = self._get_required_env('MINIO_ENDPOINT')
    self.minio_login = self._get_required_env('MINIO_LOGIN')
    self.minio_password = self._get_required_env('MINIO_PASSWORD')
    self.iceberg_catalog_endpoint = os.getenv('ICEBERG_CATALOG_ENDPOINT')
    self.iceberg_warehouse = os.getenv('ICEBERG_WAREHOUSE', 'prefect')
    self.iceberg_catalog_name = os.getenv('ICEBERG_CATALOG_NAME', 'lakehouse')
    self.iceberg_token = os.getenv('ICEBERG_TOKEN')

  @staticmethod
  def _get_required_env(variable: str) -> str:
    """Obtém uma variável obrigatória sem incluir seu valor em erros."""

    value = os.getenv(variable)
    if value is None or not value.strip():
      raise ConfigError(
        f"Variável de ambiente obrigatória não configurada: {variable}"
      )
    return value.strip()
