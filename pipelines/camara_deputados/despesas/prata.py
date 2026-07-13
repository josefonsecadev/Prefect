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

    Responsável pela descompactação e publicação em uma tabela Iceberg.
    """

    def __init__(self):
        super().__init__(
            Info.PROJECT_NAME,
            Info.PIPELINE_NAME, 
            "prata"
        )

    @flow(
        name="camara_despesas_prata",
        description="Lê a camada bronze e publica um snapshot Iceberg.",
        log_prints=True
    )
    def execute(self, year: int | None = None):
        resolved_year = resolve_year(year)
        self.log.info(f"[PRATA] INICIANDO PUBLICAÇÃO ICEBERG DE {resolved_year}")

        despesa_bytes = self._read_bronze(resolved_year)

        self._transform_table("despesas", despesa_bytes, resolved_year)

        snapshot = self._save_iceberg(
            tabela_origem="despesas",
            tabela_destino="despesas",
            schema=Info.SCHEMA_PRATA,
            partition=["numAno"],
            replace_by={"numAno": str(resolved_year)}
        )

        self.log.info(f"[PRATA] SNAPSHOT ICEBERG PUBLICADO: {snapshot}")

    @task
    def _read_bronze(self, year: int) -> BytesIO:
        """
        Faz a leitura da camada bronze da pipeline e retorna o arquivo.
        """
        bronze = PipeBronze()
        return bronze._read_arquivo(str(year))

    @task
    def _transform_table(self,
                         tabela: str,
                         zip_bytes: BytesIO,
                         year: int):
        """
        Transforma o zip em dataframe duckdb.
        """
        with zipfile.ZipFile(zip_bytes) as zf:
            with zf.open(f"Ano-{year}.csv") as csv_file:
                conteudo = BytesIO(csv_file.read())
                self.csv_to_duckdb(tabela, conteudo=conteudo)
