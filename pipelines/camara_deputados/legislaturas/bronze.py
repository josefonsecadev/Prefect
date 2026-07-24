from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import requests
from prefect import flow, task

from utils.camara import Camara
from utils.pipeline import Pipeline

try:
    from .info import Info
except ImportError:  # pragma: no cover
    from info import Info


class PipeBronze(Pipeline):
    """Coleta uma página de legislaturas e a persiste em Parquet."""

    def __init__(self):
        super().__init__(Info.PROJECT_NAME, Info.PIPELINE_NAME, "bronze")

    @flow(
        name="camara_legislaturas_bronze",
        description="Coleta até 100 legislaturas e salva um único Parquet.",
        log_prints=True,
    )
    def execute(self) -> int:
        self.log.info("[BRONZE] INICIANDO COLETA DAS LEGISLATURAS")
        quantidade = self._coletar_legislaturas()
        self.log.info(
            "[BRONZE] FINALIZANDO COLETA DAS LEGISLATURAS: %s registros",
            quantidade,
        )
        return quantidade

    @task(name="coletar_legislaturas")
    def _coletar_legislaturas(self) -> int:
        resposta = requests.get(
            Camara().legislaturas,
            params={"pagina": 1, "itens": 100},
            timeout=(5, 30),
        )
        resposta.raise_for_status()

        content_type = resposta.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            raise ValueError(
                "Resposta de legislaturas fora do contrato: "
                f"Content-Type {content_type or 'ausente'}"
            )

        try:
            payload = resposta.json()
        except requests.JSONDecodeError as erro:
            raise ValueError("Resposta de legislaturas não contém JSON válido") from erro

        dados = payload.get("dados") if isinstance(payload, dict) else None
        if not isinstance(dados, list) or not dados:
            raise ValueError(
                "Resposta de legislaturas fora do contrato: 'dados' deve ser uma lista não vazia"
            )
        if len(dados) > 100:
            raise ValueError("Resposta de legislaturas excedeu o limite de 100 registros")

        campos_obrigatorios = set(Info.SCHEMA)
        for indice, registro in enumerate(dados):
            if not isinstance(registro, dict):
                raise ValueError(
                    f"Registro de legislatura na posição {indice} não é um objeto"
                )
            campos_faltando = campos_obrigatorios - registro.keys()
            if campos_faltando:
                raise ValueError(
                    "Resposta de legislaturas fora do contrato: campos ausentes "
                    f"{sorted(campos_faltando)} no registro {indice}"
                )

        parquet = self._converter_para_parquet(dados)
        self._salva_arquivos(
            arquivo=parquet,
            nome_arquivo=Info.BRONZE_FILE_NAME,
            subpath=Info.BRONZE_SUBPATH,
        )
        return len(dados)

    def _converter_para_parquet(self, dados: list[dict]) -> BytesIO:
        with TemporaryDirectory() as diretorio:
            caminho_json = Path(diretorio) / "legislaturas.json"
            caminho_parquet = Path(diretorio) / Info.BRONZE_FILE_NAME
            caminho_json.write_text(
                json.dumps(dados, ensure_ascii=False),
                encoding="utf-8",
            )

            origem = self._sql_literal(str(caminho_json))
            destino = self._sql_literal(str(caminho_parquet))
            self.duckdb_conn.execute(
                f"COPY (SELECT * FROM read_json_auto({origem})) "
                f"TO {destino} (FORMAT PARQUET)"
            )
            return BytesIO(caminho_parquet.read_bytes())
