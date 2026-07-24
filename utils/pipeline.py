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
                      schema: dict[str, str] = None,
                      camada: Optional[str] = None) -> duckdb.DuckDBPyConnection:
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
    camada_origem = camada or self.camada
    with self._minio() as minio_client:
      objetos = [
          objeto for objeto in minio_client.list_objects(
              bucket_name=camada_origem,
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
        caminho = f"s3://{camada_origem}/{objeto.object_name}"

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


  def _save_iceberg(self,
                    tabela_origem: str,
                    tabela_destino: str,
                    schema: dict[str, str],
                    partition: Optional[list[str]] = None,
                    replace_by: Optional[dict[str, object]] = None,
                    replace_all: bool = False
                    ) -> dict:
    """Publica uma tabela DuckDB em Iceberg com commit transacional.

    Salva em ``camada_projeto.tabela``. Se ``replace_by`` for passado,
    somente a partição lógica indicada é substituída. Com ``replace_all``,
    substitui integralmente tabelas sem recorte. O retorno contém os metadados
    do snapshot mais recente.
    """

    if replace_by and replace_all:
      raise ValueError("replace_by e replace_all não podem ser usados juntos")

    self._apply_schema(tabela_origem, schema)
    catalog_name = self._attach_iceberg_catalog()

    catalog = self._sql_identifier(catalog_name)
    namespace = self._iceberg_namespace()
    destino_sql = self._sql_identifier(tabela_destino)
    origem_sql = self._sql_identifier(tabela_origem)
    tabela_iceberg = f"{catalog}.{namespace}.{destino_sql}"

    partition = partition or []
    colunas_invalidas = [
        coluna for coluna in [*partition, *(replace_by or {})]
        if coluna not in schema
    ]
    if colunas_invalidas:
      raise ValueError(
          f"Colunas não encontradas no schema: {', '.join(colunas_invalidas)}"
      )

    self.duckdb_conn.execute(
        f"CREATE SCHEMA IF NOT EXISTS {catalog}.{namespace}"
    )

    colunas = ", ".join(
        f"{self._sql_identifier(coluna)} {tipo}"
        for coluna, tipo in schema.items()
    )
    partition_clause = ""
    if partition:
      partition_clause = " PARTITIONED BY (" + ", ".join(
          self._sql_identifier(coluna) for coluna in partition
      ) + ")"

    self.duckdb_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {tabela_iceberg} ({colunas})"
        f"{partition_clause} WITH ('format-version' = '2')"
    )

    try:
      self.duckdb_conn.execute("BEGIN TRANSACTION")
      if replace_by:
        filtros = " AND ".join(
            f"{self._sql_identifier(coluna)} = ?" for coluna in replace_by
        )
        self.duckdb_conn.execute(
            f"DELETE FROM {tabela_iceberg} WHERE {filtros}",
            list(replace_by.values())
        )
      elif replace_all:
        self.duckdb_conn.execute(f"DELETE FROM {tabela_iceberg}")
      self.duckdb_conn.execute(
          f"INSERT INTO {tabela_iceberg} BY NAME SELECT * FROM {origem_sql}"
      )
      self.duckdb_conn.execute("COMMIT")
    except Exception:
      self.duckdb_conn.execute("ROLLBACK")
      raise

    snapshot = self.duckdb_conn.execute(
        f"SELECT * FROM iceberg_snapshots({tabela_iceberg}) "
        f"ORDER BY timestamp_ms DESC LIMIT 1"
    )
    colunas_snapshot = [descricao[0] for descricao in snapshot.description]
    valores_snapshot = snapshot.fetchone()
    return dict(zip(colunas_snapshot, valores_snapshot)) if valores_snapshot else {}


  def _iceberg_namespace(self, camada: Optional[str] = None) -> str:
    """Retorna o namespace SQL que identifica a camada e o projeto."""

    return self._sql_identifier(f"{camada or self.camada}_{self.project_name}")


  def _iceberg_snapshots(self,
                         tabela: str,
                         camada: Optional[str] = None) -> list[dict]:
    """Lista snapshots disponíveis para auditoria e time travel."""

    catalog_name = self._attach_iceberg_catalog()
    tabela_iceberg = ".".join((
        self._sql_identifier(catalog_name),
        self._iceberg_namespace(camada),
        self._sql_identifier(tabela)
    ))
    resultado = self.duckdb_conn.execute(
        f"SELECT * FROM iceberg_snapshots({tabela_iceberg}) "
        f"ORDER BY timestamp_ms DESC"
    )
    colunas = [descricao[0] for descricao in resultado.description]
    return [dict(zip(colunas, linha)) for linha in resultado.fetchall()]


  def _read_iceberg(self,
                    tabela_origem: str,
                    tabela_destino: str,
                    camada_origem: str,
                    snapshot_id: Optional[int] = None
                    ) -> duckdb.DuckDBPyConnection:
    """Materializa o estado atual ou um snapshot histórico em tabela DuckDB."""

    catalog_name = self._attach_iceberg_catalog()
    origem = ".".join((
        self._sql_identifier(catalog_name),
        self._iceberg_namespace(camada_origem),
        self._sql_identifier(tabela_origem)
    ))
    destino = self._sql_identifier(tabela_destino)
    time_travel = ""
    if snapshot_id is not None:
      if snapshot_id < 0:
        raise ValueError("snapshot_id deve ser um inteiro positivo")
      time_travel = f" AT (VERSION => {snapshot_id})"

    self.duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {destino} AS "
        f"SELECT * FROM {origem}{time_travel}"
    )
    return self.duckdb_conn
