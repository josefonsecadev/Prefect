from io import BytesIO, SEEK_END
from typing import BinaryIO, Optional, Union
import duckdb
from tempfile import NamedTemporaryFile
import os
from utils.conexoes import Conexoes
from prefect import get_run_logger

class Pipeline(Conexoes):
  """
  Classe com padrões do pipeline como funçõe gerais de escrita e leitura  
  """

  def __init__(self,
               project_name: str,
               pipeline_name: str,
               camada: str):
    """
    Inicia a classe com o nome da pipeline e a camada.
    Estes argumentos são utilizados na identificação e criação do path de salvamento

    Args:
      pipeline_name (str): Nome da pipeline
      camada (str): Nome da camada
    """

    super().__init__()
    self.project_name = project_name
    self.pipeline_name = pipeline_name
    self.camada = camada
    self.log = get_run_logger()


  def _set_path(self, subpath: str) -> str:
     """
     Define o caminho definitivo dos paths
     """
      
     path = f"{self.project_name}/{self.pipeline_name}/{subpath}" if subpath else f"{self.pipeline_name}"

     return path


  def tamanho_arquivo(self,
                    arquivo: Union[BinaryIO, BytesIO, bytes]) -> int:
      """
      Retorna o tamanho em bytes de um arquivo/stream, 
      deixando o cursor na posição original (0) ao final.

      Args:
        arquivo (Union[BinaryIO, BytesIO, bytes]): arquivo a ser consultado
      Returns:
        (int): tamanho do arquivo em inteiro
      """
      
      if isinstance(arquivo, bytes):
          return len(arquivo)

      if hasattr(arquivo, "getvalue"):
          return len(arquivo.getvalue())

      if hasattr(arquivo, "seek") and hasattr(arquivo, "tell"):
          pos_atual = arquivo.tell()
          arquivo.seek(0, SEEK_END)
          tamanho = arquivo.tell()
          arquivo.seek(pos_atual)
          return tamanho

      raise TypeError(f"Tipo de arquivo não suportado: {type(arquivo)}")


  def _limpa_pasta(self,
                   path: str) -> None:
    """
    Limpa a pasta no datalake no caminho definido pelo padrão do pipeline

    Args:
      subpath (Optional[str], optional): Subpath para limpar a pasta. Defaults to None.
    """

    with self._minio() as minio_client:
      objects_to_delete = minio_client.list_objects(
          bucket_name=self.camada,
          prefix=path,
          recursive=True
      )
      for obj in objects_to_delete:
        minio_client.remove_object(
          self.camada,
          obj.object_name
        )


  def _salva_arquivos(self, 
                      arquivo: BinaryIO,
                      nome_arquivo: str,
                      subpath: Optional[str] = None,
                      limpa_pasta: bool = True) -> None: 
    """
    Salva o arquivo no datalake no caminho definido pelo padrão do pipeline

    Args:
      arquivo (BytesIO): Arquivo a ser salvo
      nome_arquivo (str): Nome do arquivo a ser salvo
      subpath (Optional[str], optional): Subpath para salvar o arquivo. Defaults to None.
    """

    with self._minio() as minio_client:

      path = f"{self._set_path(subpath)}/{nome_arquivo}"
     
      if limpa_pasta: self._limpa_pasta(path=path)
      
      try:
         tamanho = self.tamanho_arquivo(arquivo)
         minio_client.put_object(
            bucket_name=self.camada,
            object_name=path,
            data=arquivo,
            length=tamanho
        )
      except TypeError:
         minio_client.put_object(
            bucket_name=self.camada,
            object_name=path,
            data=arquivo,
            length=-1,
            part_size=20*1024*1024 # 20mb
        )


  def _read_dataframe(self,
                      nome_tabela: str,
                      subpath: Optional[str] = None,
                      schema: dict[str, str] = None) -> duckdb.DuckDBPyConnection:
    """
    Leitura dos arquivos em uma pasta com o schema passado salvo na conexão 
    do DuckDB

    Args:
      nome_tabela (str): nome da tabela a ser salva
      subpath (str): subpath da pasta raiz
      schema (dict[str, str]): schema a ser aplicado na 
    
    Returns:
      (duckdb.DuckDBPyConnection): conexão duckdb
     """
    prefix = self._set_path(subpath)
    with self._minio() as minio_client:
      objetos = [
          objeto for objeto in minio_client.list_objects(
              bucket_name=self.camada,
              prefix=prefix,
              recursive=True
          )
          if not objeto.is_dir
      ]

    if not objetos:
      raise FileNotFoundError(f"Nenhum arquivo encontrado no path '{prefix}'")

    def identificador(valor: str) -> str:
      return f'"{valor.replace(chr(34), chr(34) * 2)}"'

    def leitor(nome_arquivo: str) -> str:
      nome = nome_arquivo.lower()
      if nome.endswith((".parquet", ".parquet.gz")):
        return "read_parquet(?)"
      if nome.endswith((".json", ".jsonl", ".ndjson", ".json.gz")):
        return "read_json_auto(?)"
      return "read_csv_auto(?)"

    tabelas_temporarias = []
    try:
      for indice, objeto in enumerate(objetos):
        tabela_temporaria = f"_pipeline_arquivo_{indice}"
        tabelas_temporarias.append(tabela_temporaria)
        caminho = f"s3://{self.camada}/{objeto.object_name}"

        try:
          self.duckdb_conn.execute(
              f"CREATE TEMP TABLE {identificador(tabela_temporaria)} AS "
              f"SELECT * FROM {leitor(objeto.object_name)}",
              [caminho]
          )
        except Exception as erro:
          raise ValueError(
              f"Não foi possível ler o arquivo '{objeto.object_name}': {erro}"
          ) from erro

        if schema:
          try:
            self._apply_schema(tabela_temporaria, schema)
          except ValueError as erro:
            raise ValueError(
                f"Schema inválido no arquivo '{objeto.object_name}': {erro}"
            ) from erro

      if schema:
        consulta = " UNION ALL ".join(
            f"SELECT * FROM {identificador(tabela)}"
            for tabela in tabelas_temporarias
        )
      else:
        consulta = " UNION ALL BY NAME ".join(
            f"SELECT * FROM {identificador(tabela)}"
            for tabela in tabelas_temporarias
        )

      self.duckdb_conn.execute(
          f"CREATE OR REPLACE TABLE {identificador(nome_tabela)} AS {consulta}"
      )
      return self.duckdb_conn
    finally:
      for tabela_temporaria in tabelas_temporarias:
        self.duckdb_conn.execute(
            f"DROP TABLE IF EXISTS {identificador(tabela_temporaria)}"
        )


  def _read_arquivo(self,
                    subpath: Optional[str] = None) -> BytesIO:
      """
      Leitura dos arquivos da pasta.

      Se encontrar mais de um arquivo no caminho informado, levanta um erro.
      Quando houver exatamente um arquivo, retorna um objeto BytesIO com o conteúdo.

      Args:
        subpath (Optional[str], optional): Subpath de leitura
      """

      with self._minio() as minio_client:
        prefix = self._set_path(subpath)
        objetos = list(minio_client.list_objects(
            bucket_name=self.camada,
            prefix=prefix,
            recursive=True
        ))

        if len(objetos) > 1:
            raise ValueError(f"Mais de um arquivo encontrado no path '{prefix}'")

        if not objetos:
            raise FileNotFoundError(f"Nenhum arquivo encontrado no path '{prefix}'")

        with minio_client.get_object(
            bucket_name=self.camada,
            object_name=objetos[0].object_name
        ) as resposta:
            return BytesIO(resposta.read())


  def csv_to_duckdb(self,
                    table_name: str,
                    conteudo: BytesIO | str) -> duckdb.DuckDBPyConnection:

    """
    Transforma o csv em uma conexão duckdb

    Args:
      table_name (str): Nome da tabela
      conteudo (BytesIO | str): Conteúdo do CSV em Bytes ou o Caminho do csv
    Returns:
      (str): Conexção duckdb com a tabela
    """

    if isinstance(conteudo, BytesIO):
      with NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp.write(conteudo.getvalue())
        tmp_path = tmp.name
      
      try: 
          self.duckdb_conn.execute(
                f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto(?)",
                [tmp_path]  
              )
      finally:
         os.remove(tmp_path)


    elif isinstance(conteudo, str):
        
        self.duckdb_conn.execute(
            f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto(?)",
            [conteudo]  
          )


  def _apply_schema(self,
                    table_name: str,
                    schema: dict[str, str]) -> duckdb.DuckDBPyConnection:
    """
    Aplica um schema em uma tabela do DuckDB.

    - Colunas presentes no dicionário `schema` são mantidas e convertidas (CAST)
      para o tipo especificado.
    - Colunas da tabela que NÃO estiverem no dicionário são removidas.
    - A ordem das colunas na tabela final segue a ordem do dicionário.

    Args:
      nome_tabela (str): Nome da tabela a ser ajustada
      schema (dict): Formato {"nome_coluna": "TIPO_SQL"}
                   ex: {"id": "BIGINT", "nome": "VARCHAR", "valor": "DOUBLE"}
    """

    colunas_atuais = {
        row[0] for row in self.duckdb_conn.execute(f"DESCRIBE {table_name}").fetchall()
    }

    colunas_faltando = set(schema.keys()) - colunas_atuais
    if colunas_faltando:
        raise ValueError(
            f"As colunas {colunas_faltando} não existem na tabela '{table_name}'"
        )

    selects = [
        f'CAST("{coluna}" AS {tipo}) AS "{coluna}"'
        for coluna, tipo in schema.items()
    ]

    select_clause = ", ".join(selects)

    query = f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT {select_clause}
        FROM {table_name}
    """

    self.duckdb_conn.execute(query)


  def _save_parquet(self,
                    tabela: str,
                    schema: dict[str, str],
                    subpath: Optional[str] = None,
                    partition: Optional[list] = None):
     
      """
      Aplica o schema passado e salva os arquivos em formato .parquet
      no diretório raiz da camada e da pipeline (ou com subpath se passado)

      Se passado partition, faz o partition_by das colunas mantendo-as no 
      dataframe

      Args:
      tabela (str): nome da tabela usada no caminho de salvamento
      schema (dict[str, str]): dict com nome da coluna e tipo SQL
      subpath (Optional[str]): subpath adicionado ao fim da camada e pipeline name
      """

      if partition:
         #TODO criar o partition_by
         pass


      self._apply_schema(
         tabela,
         schema
      )

      self.duckdb_conn.execute(f"""
          COPY {tabela}
          TO 's3://{self.camada}/{self._set_path(subpath)}/{tabela}.parquet'
          (FORMAT PARQUET)
      """)
