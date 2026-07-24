from __future__ import annotations

from prefect import flow, task

from utils.pipeline import Pipeline

try:
    from .info import Info
except ImportError:  # pragma: no cover
    from info import Info


class PipePrata(Pipeline):
    """Publica na Prata o mesmo contrato recebido na Bronze."""

    def __init__(self):
        super().__init__(Info.PROJECT_NAME, Info.PIPELINE_NAME, "prata")

    @flow(
        name="camara_legislaturas_prata",
        description="Publica o Parquet Bronze em uma tabela Iceberg sem regra de negócio.",
        log_prints=True,
    )
    def execute(self) -> dict:
        self.log.info("[PRATA] INICIANDO PUBLICAÇÃO DAS LEGISLATURAS")
        snapshot = self._publicar_legislaturas()
        self.log.info("[PRATA] SNAPSHOT ICEBERG PUBLICADO: %s", snapshot)
        return snapshot

    @task(name="publicar_legislaturas")
    def _publicar_legislaturas(self) -> dict:
        self._read_dataframe(
            nome_tabela=Info.PIPELINE_NAME,
            subpath=Info.BRONZE_SUBPATH,
            schema=Info.SCHEMA,
            camada="bronze",
        )
        return self._save_iceberg(
            tabela_origem=Info.PIPELINE_NAME,
            tabela_destino=Info.PIPELINE_NAME,
            schema=Info.SCHEMA,
            replace_all=True,
        )
