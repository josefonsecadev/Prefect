from __future__ import annotations

import zipfile
from io import BytesIO

from prefect import flow, task

from utils.pipeline import Pipeline

try:
    from .bronze import PipeBronze, resolve_year
    from .info import Info
except ImportError:  # pragma: no cover
    from bronze import PipeBronze, resolve_year
    from info import Info


class PipePrata(Pipeline):
    """
    Classe da pipeline de despesas na camada prata,

    Responsável pela descompactação do arquivo e salva-lo em formato parquet no datalake.
    """

    def __init__(self):
        super().__init__(
            Info.PROJECT_NAME,
            Info.PIPELINE_NAME, 
            "prata"
        )
        self.year = resolve_year(resolve_year())

    @flow(
        name="camara_despesas_prata",
        description="Lê a camada bronze e transforma em parquet para o ano informado.",
        log_prints=True
    )
    def execute(self, year: int | None = None):
        self.log.info("[PRATA] INCIANDO SALVAMENTO EM PARQUET COM SCHEMA")

        despesa_bytes = self._read_bronze()

        self._transform_table("despesas", despesa_bytes)

        self._save_parquet(
            "despesas",
            Info.SCHEMA_PRATA,
            subpath=str(self.year),
        )
        
        self.log.info("[PRATA] FINALIZANDO SALVAMENTO EM PARQUET COM SCHEMA")
    @task
    def _read_bronze(self) -> BytesIO:
        """
        Faz a leitura da camada bronze da pipeline e retorna o arquivo.
        """
        bronze = PipeBronze()
        return bronze._read_arquivo(str(self.year))

    @task
    def _transform_table(self,
                         tabela: str,
                         zip_bytes: BytesIO):
        """
        Transforma o zip em dataframe duckdb.
        """
        with zipfile.ZipFile(zip_bytes) as zf:
            with zf.open(f"Ano-{str(self.year)}.csv") as csv_file:
                conteudo = BytesIO(csv_file.read())
                self.csv_to_duckdb(tabela, conteudo=conteudo)
