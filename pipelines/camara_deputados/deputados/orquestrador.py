from prefect import flow
from datetime import datetime
from typing import List

try:
    from .bronze import PipeBronze
except ImportError:  # pragma: no cover
    from bronze import PipeBronze

def resolve_year(year: int | List[int] | None = None) -> tuple:
    if isinstance(year, list):
        parametro = [(str(ano) + '-01-01', str(ano) + '-12-31') for ano in year]

    elif isinstance(year, int):
        parametro = (str(year) + '-01-01', str(year) + '-12-31')
    else:
        parametro = (str(datetime.now().year) + '-01-01', str(datetime.now().year) + '-12-31')

    return parametro

@flow(
    name="camara_deputados_orquestrador",
    description="Executa as etapas bronze e prata para um ano informado.",
)
def executar_pipeline_deputados(year: int | List[int] | None = None):
    resolved_year = resolve_year(year)

    bronze = PipeBronze()
    if isinstance(resolved_year, List):
        datas_inicio = [par[0] for par in resolved_year]
        datas_fim = [par[1] for par in resolved_year]
        bronze.execute.map(datas_inicio, datas_fim)
    else:
        bronze.execute(
            data_inicio=resolved_year[0], 
            data_fim=resolved_year[1]
        )



if __name__ == '__main__':
    executar_pipeline_deputados()
