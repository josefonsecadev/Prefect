class Info:
  """
  Classe com as informações gerais do pipeline de despesas da câmara dos deputados
  """
  PROJECT_NAME = "camara_deputados"
  PIPELINE_NAME = "deputados"

  SCHEMA_BRONZE = {
    "id": "BIGINT",
    "uri": "VARCHAR",
    "nome": "VARCHAR",
    "siglaPartido": "VARCHAR",
    "uriPartido": "VARCHAR",
    "siglaUf": "VARCHAR",
    "idLegislatura": "BIGINT",
    "urlFoto": "VARCHAR",
    "email": "VARCHAR"
  }

  SCHEMA_PRATA = {
    **SCHEMA_BRONZE,
    "ano_referencia": "INTEGER"
  }
