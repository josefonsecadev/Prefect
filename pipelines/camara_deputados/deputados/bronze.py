from __future__ import annotations

from io import BytesIO
import json

import requests
from prefect import flow, task

from utils.camara import Camara
from utils.pipeline import Pipeline

try:
    from .info import Info
except ImportError:  # pragma: no cover
    from info import Info


class PipeBronze(Pipeline):
    """Coleta os deputados de uma legislatura e preserva o JSON na Bronze."""

    def __init__(self):
        super().__init__(Info.PROJECT_NAME, Info.PIPELINE_NAME, "bronze")

    @flow(
        name="camara_deputados_bronze",
        description="Coleta os deputados da legislatura informada.",
        log_prints=True,
    )
    def execute(self, id_legislatura: int) -> int:
        self.log.info(
            "[BRONZE] INICIANDO COLETA DA LEGISLATURA %s", id_legislatura
        )
        quantidade = self._coletar_deputados(id_legislatura)
        self.log.info(
            "[BRONZE] FINALIZANDO COLETA DA LEGISLATURA %s: %s registros",
            id_legislatura,
            quantidade,
        )
        return quantidade

    @task(name="coletar_deputados")
    def _coletar_deputados(self, id_legislatura: int) -> int:
        pagina = 1
        quantidade = 0
        camara = Camara()

        while True:
            resposta = requests.get(
                camara.deputados,
                params={
                    "idLegislatura": id_legislatura,
                    "pagina": pagina,
                    "itens": 100,
                },
                timeout=(5, 30),
            )
            resposta.raise_for_status()

            content_type = resposta.headers.get("content-type", "").lower()
            if "application/json" not in content_type:
                raise ValueError(
                    "Resposta de deputados fora do contrato: "
                    f"Content-Type {content_type or 'ausente'}"
                )

            payload = resposta.json()
            dados = payload.get("dados") if isinstance(payload, dict) else None
            if not isinstance(dados, list):
                raise ValueError(
                    "Resposta de deputados fora do contrato: 'dados' deve ser uma lista"
                )
            if not dados:
                break

            ids_recebidos = {registro.get("idLegislatura") for registro in dados}
            if ids_recebidos != {id_legislatura}:
                raise ValueError(
                    "A API retornou deputados fora da legislatura solicitada: "
                    f"esperada={id_legislatura}, recebidas={sorted(ids_recebidos)}"
                )

            conteudo = BytesIO(
                json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")
            )
            self._salva_arquivos(
                arquivo=conteudo,
                nome_arquivo="deputados.json",
                subpath=f"idLegislatura={id_legislatura}/pagina={pagina}",
            )
            quantidade += len(dados)
            self.log.info(
                "[BRONZE] LEGISLATURA %s, PÁGINA %s: %s REGISTROS",
                id_legislatura,
                pagina,
                len(dados),
            )

            if len(dados) < 100:
                break
            pagina += 1

        if quantidade == 0:
            raise ValueError(
                f"A API não retornou deputados para a legislatura {id_legislatura}"
            )
        return quantidade
