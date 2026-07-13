from __future__ import annotations

from prefect import flow, task

from utils.pipeline import Pipeline

try:
    from .info import Info
except ImportError:  # pragma: no cover
    from info import Info


class PipePrata(Pipeline):
    """Consolida os arquivos bronze de deputados em um Parquet por ano."""

    def __init__(self):
        super().__init__(
            Info.PROJECT_NAME,
            Info.PIPELINE_NAME,
            "prata"
        )

    @flow(
        name="camara_deputados_prata",
        description="Lê os JSONs bronze, aplica o schema e salva um Parquet.",
        log_prints=True
    )
    def execute(self, year: int):
        self.log.info(f"[PRATA] INICIANDO CONSOLIDAÇÃO DOS DEPUTADOS DE {year}")

        self._consolidar_ano(year)

        self.log.info(f"[PRATA] FINALIZANDO CONSOLIDAÇÃO DOS DEPUTADOS DE {year}")

    @task
    def _consolidar_ano(self, year: int) -> None:
        subpath = f"ano={year}"
        self._read_dataframe(
            nome_tabela="deputados",
            subpath=subpath,
            schema=Info.SCHEMA_PRATA,
            camada="bronze"
        )
        self._save_parquet(
            tabela="deputados",
            schema=Info.SCHEMA_PRATA,
            subpath=subpath
        )
