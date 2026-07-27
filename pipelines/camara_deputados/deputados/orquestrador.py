from __future__ import annotations

from prefect import flow

from utils.pipeline import Pipeline

try:
    from .bronze import PipeBronze
    from .prata import PipePrata
except ImportError:  # pragma: no cover
    from bronze import PipeBronze
    from prata import PipePrata


class ConsultaLegislaturas(Pipeline):
    """Resolve os recortes do flow pela tabela Prata de legislaturas."""

    def __init__(self):
        super().__init__("camara_deputados", "legislaturas", "prata")

    def resolver(self, ano_inicial: int | None, ano_final: int | None) -> list[int]:
        if (ano_inicial is None) != (ano_final is None):
            raise ValueError("ano_inicial e ano_final devem ser informados juntos")
        if ano_inicial is not None and ano_inicial > ano_final:
            raise ValueError("ano_inicial não pode ser maior que ano_final")

        self._read_iceberg(
            tabela_origem="legislaturas",
            tabela_destino="_legislaturas_disponiveis",
            camada_origem="prata",
        )

        if ano_inicial is None:
            linhas = self.duckdb_conn.execute(
                "SELECT id FROM _legislaturas_disponiveis "
                "ORDER BY id DESC LIMIT 1"
            ).fetchall()
        else:
            linhas = self.duckdb_conn.execute(
                """
                SELECT id
                FROM _legislaturas_disponiveis
                WHERE dataInicio <= make_date(?, 12, 31)
                  AND COALESCE(dataFim, DATE '9999-12-31') >= make_date(?, 1, 1)
                ORDER BY id
                """,
                [ano_final, ano_inicial],
            ).fetchall()

        ids = [int(linha[0]) for linha in linhas]
        if not ids:
            recorte = (
                "mais recente"
                if ano_inicial is None
                else f"intervalo {ano_inicial}-{ano_final}"
            )
            raise ValueError(f"Nenhuma legislatura encontrada para o recorte {recorte}")
        return ids


@flow(
    name="camara_deputados_orquestrador",
    description="Executa Bronze e Prata para as legislaturas resolvidas pela tabela Prata.",
    log_prints=True,
)
def executar_pipeline_deputados(
    ano_inicial: int | None = None,
    ano_final: int | None = None,
) -> dict:
    ids_legislaturas = ConsultaLegislaturas().resolver(ano_inicial, ano_final)
    print(f"[ORQUESTRADOR] LEGISLATURAS SELECIONADAS: {ids_legislaturas}")

    bronze = PipeBronze()
    prata = PipePrata()
    resultados = []

    for id_legislatura in ids_legislaturas:
        quantidade = bronze.execute(id_legislatura=id_legislatura)
        snapshot = prata.execute(id_legislatura=id_legislatura)
        resultados.append(
            {
                "id_legislatura": id_legislatura,
                "quantidade_bronze": quantidade,
                "snapshot_prata": snapshot,
            }
        )

    return {"legislaturas": resultados}


if __name__ == "__main__":
    executar_pipeline_deputados()
