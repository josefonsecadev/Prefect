"""Produto analítico: despesas líquidas mensais por deputado."""
from prefect import flow

from utils.pipeline import Pipeline
from .info import Info


class PipeOuro(Pipeline):
    def __init__(self):
        super().__init__(Info.PROJECT_NAME, Info.PIPELINE_NAME, "ouro")

    @flow(name="camara_despesas_ouro", log_prints=True)
    def execute(self, year: int) -> dict:
        source = self._iceberg_table_identifier("despesas", "prata")
        # Filtrar antes de materializar: não carregar todos os anos na memória.
        self.duckdb_conn.execute(
            f"CREATE TEMP TABLE despesas_recorte AS SELECT "
            "CAST(numAno AS INTEGER) AS ano, CAST(numMes AS INTEGER) AS mes, "
            "NULLIF(TRIM(ideCadastro), '') AS deputado_id, "
            "txNomeParlamentar AS nome, "
            "CAST(REPLACE(TRIM(vlrLiquido), ',', '.') AS DECIMAL(18,2)) AS valor "
            f"FROM {source} WHERE numAno = ?", [str(year)],
        )
        invalid = self.duckdb_conn.execute(
            "SELECT count(*) FROM despesas_recorte WHERE deputado_id IS NULL "
            "OR mes IS NULL OR mes NOT BETWEEN 1 AND 12 OR valor IS NULL"
        ).fetchone()[0]
        total = self.duckdb_conn.execute("SELECT count(*) FROM despesas_recorte").fetchone()[0]
        if not total or invalid:
            raise ValueError(f"Recorte Ouro inválido: {total} lançamentos, {invalid} registros inválidos")
        self.duckdb_conn.execute(
            "CREATE TEMP TABLE despesas_mensais AS SELECT ano, mes, deputado_id, "
            "MIN(nome) AS nome_deputado, COUNT(*) AS quantidade_lancamentos, "
            "CAST(SUM(valor) AS DECIMAL(18,2)) AS valor_liquido "
            "FROM despesas_recorte GROUP BY ano, mes, deputado_id"
        )
        expected = self.duckdb_conn.execute("SELECT SUM(valor), COUNT(*) FROM despesas_recorte").fetchone()
        actual = self.duckdb_conn.execute(
            "SELECT SUM(valor_liquido), SUM(quantidade_lancamentos) FROM despesas_mensais"
        ).fetchone()
        if actual != expected:
            raise ValueError("Reconciliação Prata/Ouro falhou")
        snapshot = self._save_iceberg(
            tabela_origem="despesas_mensais", tabela_destino="despesas_mensais",
            schema=Info.SCHEMA_OURO, partition=["ano"], replace_by={"ano": year},
        )
        self.log.info("Ouro publicada: ano=%s lançamentos=%s valor=%s snapshot=%s",
                      year, total, actual[0], snapshot)
        return snapshot
