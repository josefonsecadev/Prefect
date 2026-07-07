class Info:
  """
  Classe com as informações gerais do pipeline de despesas da câmara dos deputados
  """
  PROJECT_NAME = "camara_deputados"
  PIPELINE_NAME = "despesas"
  

  SCHEMA_PRATA = {
    "txNomeParlamentar": "VARCHAR",
    "cpf": "VARCHAR",
    "ideCadastro": "VARCHAR",
    "nuCarteiraParlamentar": "VARCHAR",
    "nuLegislatura": "VARCHAR",
    "sgUF": "VARCHAR",
    "sgPartido": "VARCHAR",
    "codLegislatura": "VARCHAR",
    "numSubCota": "VARCHAR",
    "txtDescricao": "VARCHAR",
    "numEspecificacaoSubCota": "VARCHAR",
    "txtDescricaoEspecificacao": "VARCHAR",
    "txtFornecedor": "VARCHAR",
    "txtCNPJCPF": "VARCHAR",
    "txtNumero": "VARCHAR",
    "indTipoDocumento": "VARCHAR",
    "datEmissao": "VARCHAR",
    "vlrDocumento": "VARCHAR",
    "vlrGlosa": "VARCHAR",
    "vlrLiquido": "VARCHAR",
    "numMes": "VARCHAR",
    "numAno": "VARCHAR",
    "numParcela": "VARCHAR",
    "txtPassageiro": "VARCHAR",
    "txtTrecho": "VARCHAR",
    "numLote": "VARCHAR",
    "numRessarcimento": "VARCHAR",
    "datPagamentoRestituicao": "VARCHAR",
    "vlrRestituicao": "VARCHAR",
    "nuDeputadoId": "VARCHAR",
    "ideDocumento": "VARCHAR",
    "urlDocumento": "VARCHAR"
  }