# Lakehouse da Câmara dos Deputados

Pipelines Python/Prefect coletam dados da Câmara, transformam com DuckDB e
publicam tabelas Iceberg no RustFS. Nessie mantém o catálogo Iceberg REST e
ClickHouse oferece consultas SQL de leitura para consumidores.

```text
Fontes → Bronze (RustFS) → Prata/Ouro (Iceberg no RustFS)
                                  ↑ catálogo Nessie
                                  ↓ consultas SQL
                              ClickHouse
```

## Estado

A substituição de Polaris/PostgreSQL/Trino por Nessie/ClickHouse está em andamento
(TASK-0025). Integrações de Iceberg com Nessie e ClickHouse devem ser validadas no
ambiente Docker; confira o estado atualizado em [.agents/tasks/README.md](.agents/tasks/README.md).
Os limites de memória do Compose ainda não comprovam capacidade total de 2GB.

O flow de Legislaturas já grava Iceberg pelo Nessie. O ClickHouse lista a tabela,
mas a leitura via catálogo falha com HTTP 403 no RustFS por uma incompatibilidade
aberta no `DataLakeCatalog`; portanto, o acesso SQL às tabelas ainda não está pronto.

## Configuração

O projeto usa um `.env` fixo, ignorado pelo Git. Preserve o arquivo e as credenciais
locais existentes. Em nova instalação, copie `.env.example` para `.env` e configure
os segredos de RustFS/S3 e ClickHouse. `S3_ACCESS_KEY`/`S3_SECRET_KEY` precisam ter
acesso de leitura e escrita ao bucket `iceberg`; `RUSTFS_ACCESS_KEY`/
`RUSTFS_SECRET_KEY` são as credenciais administrativas do serviço. Não versionar
`.env`, certificados ou chaves.

O novo warehouse Nessie usa `s3://iceberg/nessie-warehouse`, separado dos objetos
legados em `s3://iceberg/warehouse`. Volumes antigos de PostgreSQL/Polaris, se
existirem, não são montados nem removidos. Não execute `down -v` para reiniciar.

Pré-requisitos: Docker com engine Linux, Compose V2, Python 3.14.6 e Poetry para
execução/debug no host.

```powershell
$env:POETRY_VIRTUALENVS_IN_PROJECT='true'
poetry install --no-root
docker compose --profile processing up --build -d
```

O Compose inicia RustFS, Nessie, ClickHouse, Prefect Server e Worker. Server e
Worker permanecem ligados; deployments são registrados pelo Worker. Para verificar:

```powershell
docker compose --profile processing ps
```

Endpoints locais: Prefect `http://localhost:4200`, Nessie
`http://localhost:19120/iceberg`, ClickHouse HTTP `localhost:8123`, ClickHouse
Native `localhost:9002`, RustFS S3 `localhost:9000` e console `localhost:9001`.
Dentro dos containers, os hosts são `prefect-server`, `nessie` e `rustfs`.

## Flows

Os perfis do VS Code em `.vscode/launch.json` usam o `.env` e o ambiente `.venv`.
Execute um flow por vez. Legislaturas deve preceder Deputados. Despesas percorre
Bronze → Prata → Ouro.

```powershell
./.venv/Scripts/python.exe -m pipelines.camara_deputados.legislaturas.orquestrador
./.venv/Scripts/python.exe -m pipelines.camara_deputados.deputados.orquestrador
./.venv/Scripts/python.exe -m pipelines.camara_deputados.despesas.orquestrador
```

O formato `PIPELINE_STORAGE_FORMAT=iceberg` usa Nessie. O modo `parquet` legado
publica arquivos diretamente e não oferece catálogo ou snapshots Iceberg. Em
execuções anteriores (TASK-0019), Despesas 2025 concluiu Bronze/Prata, mas Ouro
falhou para 937 registros sem ID de deputado; Legislaturas e Deputados também
falharam na API/pré-requisitos. Esses resultados não validam os flows completos.

## Consultar a Ouro

O acesso por nome no catálogo ClickHouse/Nessie ainda não está disponível. A leitura
Iceberg direta foi validada com `icebergS3()` usando o caminho completo da tabela no
RustFS e o usuário administrativo do ClickHouse. Exemplo:

```sql
SELECT count(), min(id), max(id)
FROM icebergS3('http://rustfs:9000/iceberg/nessie-warehouse/<namespace>/<tabela>/');
```

O teste na tabela `prata_camara_deputados.legislaturas` retornou 57 linhas (IDs 1–57).
O perfil `analista` não pode executar essa função em `readonly=1`; não compartilhe
credenciais administrativas com consumidores. A descoberta automática do path pelo
Nessie e a exposição somente leitura por nome continuam pendentes na TASK-0025.

Quando esse acesso estiver pronto, a consulta esperada da Ouro será:

```sql
SELECT ano, mes, deputado_id, nome_deputado,
       quantidade_lancamentos, valor_liquido
FROM lakehouse.`ouro_camara_deputados.despesas_mensais`
WHERE ano = 2025
ORDER BY valor_liquido DESC;
```

O catálogo ClickHouse é configurado como leitura; consumidores SQL não recebem
credenciais S3. Confirme a compatibilidade de autenticação e do catálogo na versão
fixada antes de oferecer acesso fora do host local.

## Dados e manutenção

Volumes nomeados: `rustfs-data`, `nessie-data`, `clickhouse-data` e `prefect-data`.
O warehouse Nessie é novo; os objetos e o catálogo legado permanecem preservados,
mas não são importados automaticamente. Faça backup antes de operações de
manutenção. `docker compose stop` preserva os dados; não remova volumes para
reiniciar serviços.
