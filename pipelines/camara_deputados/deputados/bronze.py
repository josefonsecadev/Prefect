from __future__ import annotations

from io import BytesIO
import json

import requests
from prefect import flow, task

from utils.camara import Camara
from utils.pipeline import Pipeline

try:
    from .info import Info
except ImportError:
    from info import Info




class PipeBronze(Pipeline):
    """
    Classe da pipeline de deputados na camada bronze,

    Responsável pela extração dos dados da API com parâmetro ano 
    e salvar no datalake em format json.
    """

    def __init__(self):
        super().__init__(
            Info.PROJECT_NAME,
            Info.PIPELINE_NAME, 
            "bronze")

    @flow(
        name="camara_deputados_bronze",
        description="Baixa o json correspondente aos deputados em exercício no ano do parâmetro.",
        log_prints=True
    )
    def execute(self, data_inicio: str, data_fim: str):
        self.log.info(f"[BRONZE] INCIANDO COLETA DOS DEPUTADOS DAS DATAS {data_inicio} ATÉ {data_fim}")

        self._download_expenses_file(data_inicio, data_fim)

        self.log.info(f"[BRONZE] FNALIZANDO COLETA DOS DEPUTADOS DAS DATAS {data_inicio} ATÉ {data_fim}")

    @task
    def _download_expenses_file(self, data_inicio: str, data_fim: str):
        """
        Faz dos deputados no ano referencia
        Endpoint: /deputados
        .

        Args:
            data_inicio (str): primeiro dia do ano.
            data_fim (str): último dia do ano
        """
        camara = Camara()
        pagina = 1
        while True:
            request = requests.get(
                camara.deputados,
                params={
                    "pagina": pagina,
                    "itens": 100,
                    "dataInicio": data_inicio,
                    "dataFim": data_fim
                })
             
            if int(request.headers.get("x-total-count")) > 0:
                conteudo = BytesIO(
                    json.dumps(
                        request.json().get('dados'),
                        ensure_ascii=False,
                        indent=2
                    ).encode("utf-8")
                )
                
                self._salva_arquivos(
                    arquivo = conteudo,
                    nome_arquivo = f"deputados.json",
                    subpath = f'ano={data_inicio[:4]}/pagina={pagina}'
                )

                self.log.info(f"[BRONZE] EXECUÇÃO DA PÁGINA {pagina} CONCLUÍDA COM SUCESSO...")

                pagina += 1
            else:
                break
                