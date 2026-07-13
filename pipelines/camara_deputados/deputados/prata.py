from __future__ import annotations

from prefect import flow, task

from utils.pipeline import Pipeline

try:
    from .info import Info
except ImportError:  # pragma: no cover
    from info import Info


class PipePrata(Pipeline):
    """Consolida os arquivos bronze em uma tabela Iceberg particionada."""

    def __init__(self):
        super().__init__(
            Info.PROJECT_NAME,
            Info.PIPELINE_NAME,
            "prata"
        )

    @flow(
        name="camara_deputados_prata",
        description="Lê os JSONs bronze e publica um snapshot Iceberg.",
        log_prints=True
    )
    def execute(self, year: int):
        self.log.info(f"[PRATA] INICIANDO CONSOLIDAÇÃO DOS DEPUTADOS DE {year}")

        snapshot = self._consolidar_ano(year)
        self.log.info(f"[PRATA] SNAPSHOT ICEBERG PUBLICADO: {snapshot}")

        self.log.info(f"[PRATA] FINALIZANDO CONSOLIDAÇÃO DOS DEPUTADOS DE {year}")

    @task
    def _consolidar_ano(self, year: int) -> dict:
        subpath = f"ano={year}"
        self._read_dataframe(
            nome_tabela="deputados",
            subpath=subpath,
            schema=Info.SCHEMA_BRONZE,
            camada="bronze"
        )
        self.duckdb_conn.execute(
            "ALTER TABLE deputados ADD COLUMN ano_referencia INTEGER"
        )
        self.duckdb_conn.execute(
            "UPDATE deputados SET ano_referencia = ?",
            [year]
        )

        return self._save_iceberg(
            tabela_origem="deputados",
            tabela_destino="deputados",
            schema=Info.SCHEMA_PRATA,
            partition=["ano_referencia"],
            replace_by={"ano_referencia": year}
        )
