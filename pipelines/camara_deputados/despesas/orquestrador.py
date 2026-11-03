from prefect import flow

try:
    from .bronze import PipeBronze, resolve_year
    from .prata import PipePrata
    from .ouro import PipeOuro
except ImportError:  # pragma: no cover
    from bronze import PipeBronze, resolve_year
    from prata import PipePrata
    from ouro import PipeOuro


@flow(
    name="camara_despesas_orquestrador",
    description="Executa Bronze, Prata e Ouro para um ano informado.",
)
def executar_pipeline_despesas(year: int | None = None):
    resolved_year = resolve_year(year)

    bronze = PipeBronze()
    prata = PipePrata()

    bronze.execute(year=resolved_year)
    prata.execute(year=resolved_year)
    return PipeOuro().execute(year=resolved_year)


if __name__ == '__main__':
    executar_pipeline_despesas()
