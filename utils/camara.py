from __future__ import annotations


class Camara:
    """
    Classe que representa as urls essenciais para consulta na API da Câmara dos Deputados.
    """

    def __init__(self,
                 url_base: str | None = None):
        self.url_base = url_base or "https://dadosabertos.camara.leg.br/api/v2/"
        self.url_despesas_ano = "http://www.camara.leg.br/cotas/Ano-{ano}.csv.zip"  