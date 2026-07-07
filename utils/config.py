from dotenv import load_dotenv
import os


class Config:
  """
  Classe por padronizar a configuração de acesso ao MiniO
  """

  def __init__(self):
    load_dotenv()
    self.ambiente = os.getenv('AMBIENTE')
    self.minio_endpoint = os.getenv('MINIO_ENDPOINT')
    self.minio_login = os.getenv('MINIO_LOGIN')
    self.minio_password = os.getenv('MINIO_PASSWORD')
