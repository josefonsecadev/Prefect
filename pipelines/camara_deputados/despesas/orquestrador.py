from prefect import flow

try:
    from .bronze import PipeBronze, resolve_year
    from .prata import PipePrata
except ImportError:  # pragma: no cover
    from bronze import PipeBronze, resolve_year
    from prata import PipePrata


@flow(
    name="camara_despesas_orquestrador",
    description="Executa as etapas bronze e prata para um ano informado.",
)
def executar_pipeline_despesas(year: int | None = None):
    resolved_year = resolve_year(year)

    bronze = PipeBronze()
    prata = PipePrata()

    bronze.execute(year=resolved_year)
    prata.execute(year=resolved_year)


if __name__ == '__main__':
    executar_pipeline_despesas()
