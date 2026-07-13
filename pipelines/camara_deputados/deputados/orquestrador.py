from datetime import datetime

from prefect import flow

try:
    from .bronze import PipeBronze
    from .prata import PipePrata
except ImportError:  # pragma: no cover
    from bronze import PipeBronze
    from prata import PipePrata


@flow(
    name="camara_deputados_orquestrador",
    description="Executa as etapas bronze e prata para os anos informados.",
)
def executar_pipeline_deputados(year: int | list[int] | None = None):
    anos = year if isinstance(year, list) else [year or datetime.now().year]

    bronze = PipeBronze()
    prata = PipePrata()

    for ano in anos:
        bronze.execute(
            data_inicio=f"{ano}-01-01",
            data_fim=f"{ano}-12-31"
        )
        prata.execute(year=ano)


if __name__ == "__main__":
    executar_pipeline_deputados()
