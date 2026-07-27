from __future__ import annotations

from prefect import flow, task

from utils.pipeline import Pipeline

try:
    from .info import Info
except ImportError:  # pragma: no cover
    from info import Info


class PipePrata(Pipeline):
    """Consolida uma legislatura em uma partição da tabela Iceberg."""

    def __init__(self):
        super().__init__(Info.PROJECT_NAME, Info.PIPELINE_NAME, "prata")

    @flow(
        name="camara_deputados_prata",
        description="Publica os deputados particionados por idLegislatura.",
        log_prints=True,
    )
    def execute(self, id_legislatura: int) -> dict:
        self.log.info(
            "[PRATA] INICIANDO CONSOLIDAÇÃO DA LEGISLATURA %s", id_legislatura
        )
        snapshot = self._consolidar_legislatura(id_legislatura)
        self.log.info("[PRATA] SNAPSHOT ICEBERG PUBLICADO: %s", snapshot)
        return snapshot

    @task(name="consolidar_legislatura")
    def _consolidar_legislatura(self, id_legislatura: int) -> dict:
        self._read_dataframe(
            nome_tabela="deputados",
            subpath=f"idLegislatura={id_legislatura}",
            schema=Info.SCHEMA_BRONZE,
            camada="bronze",
        )

        ids_recebidos = {
            int(linha[0])
            for linha in self.duckdb_conn.execute(
                "SELECT DISTINCT idLegislatura FROM deputados"
            ).fetchall()
        }
        if ids_recebidos != {id_legislatura}:
            raise ValueError(
                "A Bronze contém deputados fora da legislatura solicitada: "
                f"esperada={id_legislatura}, recebidas={sorted(ids_recebidos)}"
            )

        return self._save_iceberg(
            tabela_origem="deputados",
            tabela_destino="deputados",
            schema=Info.SCHEMA_PRATA,
            partition=["idLegislatura"],
            replace_by={"idLegislatura": id_legislatura},
        )
