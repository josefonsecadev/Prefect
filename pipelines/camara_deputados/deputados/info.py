class Info:
    """Metadados e schemas da pipeline de deputados da Câmara."""

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
        "email": "VARCHAR",
    }

    SCHEMA_PRATA = {**SCHEMA_BRONZE}
