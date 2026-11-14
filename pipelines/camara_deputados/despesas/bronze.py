from __future__ import annotations

from datetime import datetime
from io import BytesIO
import zipfile

import requests
from prefect import flow, task
from prefect.cache_policies import NO_CACHE

from utils.camara import Camara
from utils.pipeline import Pipeline

try:
    from .info import Info
except ImportError:
    from info import Info


def resolve_year(year: int | None = None) -> int:
    return year if year is not None else datetime.now().year


class PipeBronze(Pipeline):
    """
    Classe da pipeline de despesas na camada bronze,

    Responsável pela extração dos dados da API e salvar no datalake no formato CSV compactado em zip.
    """

    def __init__(self):
        super().__init__(
            Info.PROJECT_NAME,
            Info.PIPELINE_NAME, 
            "bronze")

    @flow(
        name="camara_despesas_bronze",
        description="Baixa o arquivo consolidado de despesas da Câmara para o ano informado.",
        log_prints=True
    )
    def execute(self, year: int | None = None):
        self.log.info("[BRONZE] INCIANDO COLETA DAS DESPESAS")

        resolved_year = resolve_year(year)
        self._download_expenses_file(resolved_year)

        
        self.log.info("[BRONZE] FNALIZANDO COLETA DAS DESPESAS")

    @task(cache_policy=NO_CACHE)
    def _download_expenses_file(self, year: int):
        """
        Faz a extração do ZIP contendo as despesas dos deputados no ano passado.

        Args:
            year (int): Ano para filtro de despesas.
        """
        camara = Camara()
        request = requests.get(camara.url_despesas_ano.format(ano=year), timeout=240)
        request.raise_for_status()
        arquivo = BytesIO(request.content)
        if not zipfile.is_zipfile(arquivo):
            raise ValueError(f"Resposta de despesas de {year} não contém ZIP válido")
        with zipfile.ZipFile(arquivo) as pacote:
            if f"Ano-{year}.csv" not in pacote.namelist():
                raise ValueError(f"ZIP de despesas não contém Ano-{year}.csv")
        arquivo.seek(0)
        self._salva_arquivos(
            arquivo=arquivo,
            nome_arquivo=f"despesas_{year}.csv.zip",
            subpath=str(year),
        )
