# Pipeline de dados

## Visão geral

Este projeto implementa pipelines de dados orquestradas pelo Prefect. O DuckDB
executa as transformações, o MinIO fornece armazenamento compatível com S3 e o
Apache Iceberg organiza as tabelas analíticas. O Lakekeeper é o catálogo REST
utilizado pelo Iceberg.

| Componente | Responsabilidade |
|---|---|
| Prefect Server | API, interface web, agendamentos e estado das execuções |
| Prefect Worker | Execução dos flows e tasks |
| DuckDB | Leitura, transformação e publicação dos dados |
| MinIO | Armazenamento dos arquivos brutos e das tabelas Iceberg |
| Apache Iceberg | Formato de tabela, schema, partições, snapshots e transações |
| Lakekeeper | Catálogo REST das tabelas Iceberg |
| PostgreSQL | Persistência interna do Lakekeeper |

## Arquitetura de dados

O projeto segue a arquitetura medalhão:

```text
Fonte de dados
    |
    v
Bronze no MinIO
    |  arquivos JSON, CSV e ZIP recebidos das fontes
    v
Prata no Iceberg
    |  dados tratados, tipados, particionados e versionados
    v
Ouro no Iceberg
       tabelas agregadas destinadas a APIs, dashboards e usuários finais
```

O bucket `bronze` recebe os arquivos brutos. O bucket `iceberg` contém o
warehouse gerenciado pelo Lakekeeper; não se deve criar, mover ou excluir
manualmente objetos dentro desse warehouse.

Prata e ouro são camadas lógicas representadas por namespaces no catálogo:

```text
lakehouse
├── prata
│   └── camara_deputados
│       ├── deputados
│       └── despesas
└── ouro
    └── <projeto>
        └── <tabela destinada ao consumo>
```

Somente a camada ouro deve ser disponibilizada para dashboards e usuários
finais. Em produção, consumidores devem acessar as tabelas por uma engine SQL
com permissão somente de leitura sobre ouro, sem receber credenciais diretas do
MinIO. Bronze e prata permanecem internos às pipelines.

Os buckets `prata` e `ouro` ainda são criados pelo Compose para compatibilidade,
mas as pipelines de deputados e despesas publicam a camada prata no warehouse
Iceberg.

## Iceberg e Lakekeeper

O Iceberg não é um servidor nem um banco de dados. Ele é o formato que descreve
os arquivos de uma tabela, seus schemas, partições e snapshots. Os dados das
tabelas continuam armazenados como objetos no MinIO.

O Lakekeeper é o servidor de catálogo. Ele relaciona o nome lógico de uma tabela
com seus metadados no MinIO e coordena os commits. O PostgreSQL do serviço
`lakekeeper-db` guarda somente o estado interno do catálogo; ele não armazena as
linhas de deputados ou despesas.

```text
DuckDB
   |
   | API REST Iceberg
   v
Lakekeeper --------> PostgreSQL
   |
   | dados e metadados
   v
MinIO
```

As tabelas prata atuais são:

```sql
lakehouse.prata.camara_deputados.deputados
lakehouse.prata.camara_deputados.despesas
```

Cada reprocessamento substitui somente a partição anual correspondente e gera
um novo snapshot. Exemplos de consulta no DuckDB, depois de anexar o catálogo:

```sql
SELECT *
FROM lakehouse.prata.camara_deputados.deputados;

SELECT *
FROM iceberg_snapshots(lakehouse.prata.camara_deputados.deputados)
ORDER BY timestamp_ms DESC;

SELECT *
FROM lakehouse.prata.camara_deputados.deputados
AT (VERSION => <snapshot_id>);
```

## Serviços do Docker Compose

Serviços que permanecem online:

| Serviço | Função |
|---|---|
| `prefect-server` | Interface web, API e orquestração |
| `prefect-worker` | Execução das pipelines |
| `minio` | Armazenamento de objetos |
| `lakekeeper-db` | PostgreSQL interno do catálogo |
| `lakekeeper` | Catálogo REST Iceberg |

Serviços de inicialização que encerram após executar com sucesso:

| Serviço | Função |
|---|---|
| `createbuckets` | Cria os buckets necessários no MinIO |
| `lakekeeper-migrate` | Aplica as migrações do banco do Lakekeeper |
| `lakekeeper-bootstrap` | Inicializa o catálogo e registra o warehouse |

É normal que os três serviços de inicialização apareçam com estado `Exited (0)`.

## Estrutura do projeto

```text
.
├── pipelines/
│   └── camara_deputados/
│       ├── deputados/
│       │   ├── bronze.py
│       │   ├── prata.py
│       │   ├── info.py
│       │   └── orquestrador.py
│       └── despesas/
│           ├── bronze.py
│           ├── prata.py
│           ├── info.py
│           └── orquestrador.py
├── utils/
│   ├── config.py
│   ├── conexoes.py
│   └── pipeline.py
├── docker-compose.yml
├── Dockerfile
├── prefect.yaml
└── deployment.py
```

Cada domínio de pipeline segue estas convenções:

- `bronze.py`: extração e armazenamento dos dados brutos;
- `prata.py`: transformação e publicação da tabela Iceberg;
- `ouro.py`: agregações destinadas ao consumo, quando existirem;
- `info.py`: nomes, schemas e outras definições estáticas;
- `orquestrador.py`: flow principal que encadeia as camadas;
- as classes de camada usam os nomes `PipeBronze`, `PipePrata` e `PipeOuro`;
- o método público de cada classe é `execute`, decorado com `@flow`;
- operações internas executadas pelo Prefect são decoradas com `@task`.

Funcionalidades compartilhadas ficam em `utils`:

- `Config`: leitura e validação das variáveis de ambiente;
- `Conexoes`: conexões com MinIO, DuckDB e catálogo Iceberg;
- `Pipeline`: leitura, transformação e publicação reutilizáveis.

## Execução local

### Pré-requisitos

- Docker Desktop com Docker Compose;
- Python `3.14.6` e Poetry, caso os flows também sejam executados pelo host;
- portas `4200`, `8181`, `9000` e `9001` disponíveis;
- diretório `D:/Dados` disponível para o volume local do MinIO. Em outro
  sistema operacional, ajuste o volume do serviço `minio` no
  `docker-compose.yml`.

### 1. Criar o arquivo de ambiente

No PowerShell:

```powershell
Copy-Item .env.example .env
```

Edite `.env` e substitua todos os valores `change-me`. Para o ambiente local
atual, `MINIO_LOGIN` e `MINIO_PASSWORD` devem corresponder às credenciais
`MINIO_ROOT_USER` e `MINIO_ROOT_PASSWORD`, salvo se um usuário adicional tiver
sido criado no MinIO.

A chave `LAKEKEEPER_ENCRYPTION_KEY` deve ter pelo menos 32 caracteres, ser
aleatória e permanecer estável. Alterá-la depois que o Lakekeeper armazenar
credenciais pode impedir a leitura desses segredos.

### 2. Subir a stack completa

```powershell
docker compose up --build -d
```

O Compose executará automaticamente, nesta ordem:

1. inicialização do MinIO e criação dos buckets;
2. inicialização do PostgreSQL e migração do Lakekeeper;
3. inicialização do Lakekeeper e criação do warehouse;
4. inicialização do Prefect Server;
5. criação dos deployments e inicialização do worker.

Confira os containers:

```powershell
docker compose ps -a
```

Interfaces locais:

| Serviço | Endereço padrão |
|---|---|
| Prefect | <http://localhost:4200> |
| MinIO Console | <http://localhost:9001> |
| Lakekeeper | <http://localhost:8181> |

Para acompanhar a inicialização:

```powershell
docker compose logs -f prefect-worker lakekeeper minio
```

Interrompa a visualização dos logs com `Ctrl+C`; isso não encerra os serviços.

### 3. Executar pelo Prefect

Com a stack completa online, abra a interface do Prefect, selecione um dos
deployments definidos em `prefect.yaml` e inicie uma execução informando os
parâmetros necessários.

Também é possível usar o CLI dentro do ambiente configurado:

```powershell
docker compose exec prefect-worker prefect deployment ls
```

### 4. Executar e depurar pelo Python local

Instale as dependências:

```powershell
poetry install
```

Ao executar pelo host, os nomes Docker `minio` e `lakekeeper` não são
resolvidos. Ajuste temporariamente estas variáveis no `.env`:

```env
MINIO_ENDPOINT=localhost:9000
ICEBERG_CATALOG_ENDPOINT=http://localhost:8181/catalog
```

O worker não é afetado porque o `docker-compose.yml` sobrescreve esses endpoints
dentro do container.

Para registrar a execução local no Prefect Server que está no Compose, configure
o endpoint no terminal atual:

```powershell
$env:PREFECT_API_URL = "http://localhost:4200/api"
```

Execute o ano corrente:

```powershell
poetry run python -m pipelines.camara_deputados.despesas.orquestrador
poetry run python -m pipelines.camara_deputados.deputados.orquestrador
```

Para informar um ano específico:

```powershell
poetry run python -c "from pipelines.camara_deputados.despesas.orquestrador import executar_pipeline_despesas; executar_pipeline_despesas(year=2025)"

poetry run python -c "from pipelines.camara_deputados.deputados.orquestrador import executar_pipeline_deputados; executar_pipeline_deputados(year=2025)"
```

### Depuração dentro do worker com Dev Containers

Instale no VS Code a extensão **Dev Containers**, da Microsoft. O projeto possui
uma configuração em `.devcontainer` que reutiliza o serviço `prefect-worker` do
Compose e monta o workspace local em `/app`.

1. Suba a stack com `docker compose up --build -d`;
2. abra a paleta com `F1`;
3. execute `Dev Containers: Reopen in Container`;
4. confirme que a nova janela abriu a pasta `/app` no `prefect-worker`;
5. coloque os breakpoints e selecione `Dev Container: executar flow`;
6. pressione `F5` e informe o módulo Python do flow.

Exemplos de módulos:

```text
pipelines.camara_deputados.deputados.orquestrador
pipelines.camara_deputados.despesas.orquestrador
```

Não é necessário duplicar o `launch.json`: para outro flow, informe somente o
novo módulo. O Python, as variáveis de ambiente e os nomes de rede usados na
depuração são os mesmos do worker (`minio`, `lakekeeper` e `prefect-server`).

O comando `Dev Containers: Attach to Running Container` também pode ser usado
manualmente selecionando `prefect-worker` e abrindo `/app`, mas `Reopen in
Container` é mais reproduzível porque aplica automaticamente as extensões e o
bind mount definidos no repositório.

### 5. Testar somente a infraestrutura Iceberg

Para trabalhar na publicação Iceberg sem manter Prefect Server e Worker ativos:

```powershell
docker compose up -d minio lakekeeper-db lakekeeper createbuckets lakekeeper-bootstrap
```

Esse comando também executa as dependências de migração. Depois, execute o flow
pelo Python local conforme a etapa anterior. Dependendo da configuração local do
Prefect, ele pode usar um servidor efêmero; para registrar a execução no servidor
do projeto, suba também `prefect-server` e configure `PREFECT_API_URL`. Se a
variável tiver sido configurada anteriormente e o servidor estiver desligado,
remova-a do terminal antes de usar o modo efêmero:

```powershell
Remove-Item Env:PREFECT_API_URL -ErrorAction SilentlyContinue
```

### 6. Encerrar o ambiente

Para parar os containers preservando volumes e dados:

```powershell
docker compose stop
```

Para remover os containers e a rede, preservando os volumes nomeados:

```powershell
docker compose down
```

Não use `docker compose down -v` se quiser preservar o estado do Prefect e o
banco interno do Lakekeeper. Os arquivos do MinIO permanecem no diretório
`D:/Dados` enquanto esse diretório não for removido manualmente.

## Variáveis principais

| Variável | Uso |
|---|---|
| `PREFECT_PORT` | Porta da API e interface do Prefect |
| `MINIO_ENDPOINT` | Endpoint S3 usado pelo código |
| `MINIO_LOGIN` / `MINIO_PASSWORD` | Credenciais utilizadas pelas pipelines |
| `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` | Administração e bootstrap do MinIO |
| `ICEBERG_CATALOG_ENDPOINT` | Endpoint REST do Lakekeeper |
| `ICEBERG_WAREHOUSE` | Warehouse registrado no catálogo |
| `ICEBERG_CATALOG_NAME` | Nome usado pelo DuckDB ao anexar o catálogo |
| `LAKEKEEPER_DB_PASSWORD` | Senha do PostgreSQL interno do Lakekeeper |
| `LAKEKEEPER_ENCRYPTION_KEY` | Chave de criptografia persistente do catálogo |

Consulte `.env.example` para a lista completa.
