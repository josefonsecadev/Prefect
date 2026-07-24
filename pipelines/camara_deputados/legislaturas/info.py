class Info:
    """Metadados e schema da pipeline de legislaturas da Câmara."""

    PROJECT_NAME = "camara_deputados"
    PIPELINE_NAME = "legislaturas"
    BRONZE_SUBPATH = "dados"
    BRONZE_FILE_NAME = "legislaturas.parquet"

    SCHEMA = {
        "id": "BIGINT",
        "uri": "VARCHAR",
        "dataInicio": "DATE",
        "dataFim": "DATE",
    }
