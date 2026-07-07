from prefect import flow

from pipelines.camara_deputados.despesas.orquestrador import executar_pipeline_despesas


if __name__ == "__main__":
    executar_pipeline_despesas.deploy(
        name="camara-deputados-deployment",
        description="Deployment do flow orquestrador de despesas da Câmara",
    )
