from __future__ import annotations

from prefect import flow, task

from utils.pipeline import Pipeline


class ManutencaoIceberg(Pipeline):
    """Operacoes administrativas para tabelas Iceberg."""

    def __init__(self, projeto: str, camada: str):
        super().__init__(projeto, "iceberg_particionamento", camada)

    def reparticionar(
        self,
        tabela: str,
        novas_particoes: list[str],
        motivo: str | None = None,
    ) -> dict:
        return self._reparticionar_tabela_iceberg(
            tabela=tabela,
            novas_particoes=novas_particoes,
            motivo=motivo,
        )


@task(name="reparticionar_tabela_iceberg")
def reparticionar_tabela_iceberg(
    camada: str,
    projeto: str,
    tabela: str,
    novas_particoes: list[str],
    motivo: str | None = None,
) -> dict:
    manutencao = ManutencaoIceberg(projeto=projeto, camada=camada)
    return manutencao.reparticionar(
        tabela=tabela,
        novas_particoes=novas_particoes,
        motivo=motivo,
    )


@flow(
    name="manutencao_iceberg_particionamento",
    description="Recria uma tabela Iceberg com novo particionamento e preserva a tabela antiga como deprecated.",
    log_prints=True,
)
def executar_reparticionamento_iceberg(
    camada: str,
    projeto: str,
    tabela: str,
    novas_particoes: list[str],
    motivo: str | None = None,
) -> dict:
    resultado = reparticionar_tabela_iceberg(
        camada=camada,
        projeto=projeto,
        tabela=tabela,
        novas_particoes=novas_particoes,
        motivo=motivo,
    )
    print(
        "[MANUTENCAO] TABELA REPARTICIONADA: "
        f"{resultado['camada']}_{resultado['projeto']}.{resultado['tabela']} "
        f"({resultado['registros_copiados']} registros)"
    )
    print(
        "[MANUTENCAO] TABELA ANTIGA DESATIVADA: "
        f"{resultado['tabela_desativada']}"
    )
    return resultado


if __name__ == "__main__":
    executar_reparticionamento_iceberg(
        camada="prata",
        projeto="camara_deputados",
        tabela="deputados",
        novas_particoes=["idLegislatura"],
        motivo="Migracao do particionamento legado de deputados",
    )
