# Lakehouse da Câmara dos Deputados

Pipelines Python/Prefect coletam dados da Câmara, transformam com DuckDB e publicam
tabelas Iceberg no RustFS, registradas no Apache Polaris. Trino disponibiliza SQL
somente de leitura da Ouro. PostgreSQL guarda apenas o estado interno do Polaris.

```text
Fontes → Bronze (RustFS) → Prata (Iceberg) → Ouro (Iceberg) → Trino → consumidor
                               catálogo: Apache Polaris
```

## Estado da entrega

Implementação em andamento. Configuração revisada com `docker compose config --quiet`;
flows completos, bootstrap, reinicialização, permissões SQL e orçamento de 2GB
ainda exigem validação real. A indisponibilidade do backend Docker no host impediu
esses aceites até o momento. Consulte [.agents/tasks/README.md](.agents/tasks/README.md).
Não interpretar os limites de memória abaixo como capacidade comprovada.

Bloqueio registrado no host Windows: Docker Desktop falha ao inicializar o socket
`dockerInference`; engine Linux não responde. Reparar o Docker é pré-requisito para
executar o setup e validar as tasks. Nenhum volume antigo foi apagado.

## Instalação nova

### Execução incremental com Parquet direto no RustFS

Para a validação de coleta/transformação sem Polaris ou Trino, configure no `.env`
local `PIPELINE_STORAGE_FORMAT=parquet`. O padrão da arquitetura continua `iceberg`.
O modo Parquet dispensa credenciais e autenticação do catálogo; os buckets
`bronze`, `prata` e `ouro` devem existir no RustFS, com acesso S3 pelo `.env`.
Suba somente os serviços necessários, sem iniciar bootstraps do catálogo:

```powershell
docker compose --profile processing up -d --no-deps rustfs prefect-server
```

O host deve usar `S3_ENDPOINT=localhost:9000` e
`PREFECT_API_URL=http://127.0.0.1:4200/api`. Os perfis VS Code dos três flows usam
esses endpoints e modo Parquet. Sem adaptador de debug disponível, execute os
mesmos orquestradores com `.venv/Scripts/python.exe`, uma execução por vez:

```powershell
$env:PIPELINE_STORAGE_FORMAT='parquet'
$env:S3_ENDPOINT='localhost:9000'
$env:PREFECT_API_URL='http://127.0.0.1:4200/api'
./.venv/Scripts/python.exe -m pipelines.camara_deputados.legislaturas.orquestrador
./.venv/Scripts/python.exe -c "from pipelines.camara_deputados.deputados.orquestrador import executar_pipeline_deputados; executar_pipeline_deputados(ano_inicial=2025, ano_final=2025)"
./.venv/Scripts/python.exe -c "from pipelines.camara_deputados.despesas.orquestrador import executar_pipeline_despesas; executar_pipeline_despesas(year=2025)"
```

Não prossiga para Deputados se Legislaturas falhar. Bronze mantém o contrato
existente: Legislaturas em Parquet, Deputados em JSON paginado e Despesas em ZIP
CSV. Prata/Ouro são gravadas em
`s3://<camada>/<projeto>/<pipeline>/<tabela>/<coluna>=<recorte>/data.parquet`;
tabelas integrais não possuem o trecho de partição. Escrita serial substitui
somente a chave do recorte, valida schema/contagem local e relê o Parquet remoto.
Não oferece transações multiobjeto nem snapshots do Iceberg.

Para usar deployments com o código atual:

```powershell
docker compose --profile processing build prefect-worker
docker compose --profile processing up -d --no-deps prefect-worker
```

Estado real em 2026-11-04, registrado na TASK-0019: Worker registrou deployments e
conectou; Despesas 2025 concluiu Bronze/Prata e publicou 209.081 linhas na Prata.
Ouro falhou por 937 despesas de lideranças sem ID de deputado; tratamento de
negócio ainda pendente, nenhum descarte aplicado. Legislaturas falhou por 504 da
API e Deputados pela ausência da Prata de Legislaturas. Portanto, a versão completa
dos flows ainda não tem aceite; não interpretar arquivos publicados como sucesso
do orquestrador inteiro. Catálogo/Trino não foram validados nesta fase.

Pré-requisitos: Docker com engine Linux, Compose V2, Python 3.14.6 e Poetry para
debug no host. Não é necessário copiar dados ou catálogos do ambiente anterior.
Novos volumes são usados; MinIO e Lakekeeper não integram o Compose padrão.

No PowerShell, na raiz do projeto:

```powershell
$env:POETRY_VIRTUALENVS_IN_PROJECT='true'
poetry install --no-root
```

O ambiente utiliza um `.env` local fixo, preenchido antes de iniciar o Compose.
Na instalação existente, preserve esse arquivo e suas credenciais. Para uma nova
instalação, copie `.env.example` para `.env`, preencha os segredos administrativos,
SQL e `TRINO_INTERNAL_SECRET` com valores próprios e configure `S3_ACCESS_KEY`/`S3_SECRET_KEY` com os mesmos
valores de `RUSTFS_ACCESS_KEY`/`RUSTFS_SECRET_KEY`. Não há geração automática de `.env`.
Nunca versionar `.env`, runtime, certificados ou chaves.

### Instalação inicial (somente em ambiente novo)

Antes do primeiro `up` completo, execute as etapas explícitas:

```powershell
docker compose up -d rustfs polaris-db
docker compose --profile installation run --rm polaris-bootstrap
docker compose up -d polaris
# Aguarde Polaris ficar healthy em docker compose ps.
./.venv/Scripts/python.exe -m infra.provision
./.venv/Scripts/python.exe -m infra.prepare_trino
docker compose --profile processing up --build -d
```

`infra.provision` cria buckets, catálogo, namespaces e permissões. O Polaris emite
as credenciais dos novos usuários; o comando as salva diretamente no `.env`.
Em recursos existentes, preserva as credenciais e verifica sua autenticação.
O catálogo usa `S3_INTERNAL_ENDPOINT` (padrão `rustfs:9000`) para acesso entre containers.
O comando no host usa `S3_ENDPOINT` e `ICEBERG_CATALOG_ENDPOINT` locais.

`infra.prepare_trino` prepara o hash da senha SQL e o certificado TLS local; não
sobrescreve o certificado existente. Execute-o novamente ao mudar a senha SQL.
Se alterar `TRINO_USER`, ajuste também as regras em `infra/trino/rules.json`.

### Inicialização diária

```powershell
docker compose --profile processing up -d
```

O startup não provisiona catálogo nem gera configurações. Arquivos estáticos do
Trino ficam em `infra/trino`, com referências `${ENV:...}` para segredos do `.env`.
Não repita a instalação JDBC em volumes existentes. Preserve `.env` e backups:
credenciais perdidas exigem recuperação ou rotação explícita.

O SDK Python `minio` permanece como cliente S3; não é necessário servidor MinIO.
No perfil local, credenciais de armazenamento são compartilhadas apenas pelos
backends confiáveis; identidades Polaris de escritor, leitor e administrador são
distintas. Consumidor SQL não recebe credenciais S3. Portas ficam em loopback;
publicação externa exige configuração própria de TLS e rede.

## Serviços e persistência

| Serviço | Disponibilidade | Acesso local |
|---|---|---|
| RustFS | Permanente | API localhost:9000; console localhost:9001 |
| Polaris | Permanente | http://localhost:8181/api/catalog |
| PostgreSQL | Permanente | Rede Docker, sem porta publicada |
| Trino | Permanente | https://localhost:8080 |
| Prefect Server | Permanente | http://localhost:4200 |
| Prefect Worker | Permanente | Sem porta publicada |

Volumes nomeados novos: rustfs-data, polaris-db-data e prefect-data. Os arquivos
`.prefect/runtime/trino/server.pem` e `password.db`, junto com o `.env`, também são
persistência operacional: guardar protegidos junto com backup do catálogo/storage.
Os arquivos antigos `writer.env` e `reader.env` não são mais usados.

## Executar e depurar flows

```powershell
docker compose --profile processing up -d prefect-worker
```

As dependências iniciam Server e Polaris; a instalação deve estar preparada. No VS Code, usar os perfis
de `.vscode/launch.json`, `.venv` e `.env`. No host, endpoints são localhost; dentro
do Docker, `rustfs:9000`, `polaris:8181` e `prefect-server:4200`.

Executar legislaturas antes de deputados. Despesas executa Bronze → Prata → Ouro.
Os deployments ficam em `prefect.yaml`, com concorrência do pool limitada a um.
Exemplo com o mesmo entrypoint e ambiente do perfil de debug:

```powershell
./.venv/Scripts/python.exe -m pipelines.camara_deputados.legislaturas.orquestrador
./.venv/Scripts/python.exe -m pipelines.camara_deputados.deputados.orquestrador
./.venv/Scripts/python.exe -m pipelines.camara_deputados.despesas.orquestrador
```

## Operação contínua do Prefect

Mantenha Server e Worker ativos com o comando da seção anterior. O profile
`processing` continua necessário no Compose para iniciar esses serviços.
Execute os deployments pelo Prefect; não há executor externo que ligue ou desligue
o servidor por janela. Respeite os pré-requisitos entre pipelines e execute um flow
por vez. Os scripts de execução por janela foram removidos; não há coleta automática
de memória por esse mecanismo.

Para avaliar capacidade, medir memória total do host, OOM e pico real durante
consultas/flows: somar limites de
containers não comprova que a máquina toda cabe em 2GB. DuckDB usa uma thread,
128MB de limite interno e temporários em disco; Python/buffers ficam fora desse limite.

## Consultar a Ouro

Após bootstrap e publicação real do flow de despesas:

```powershell
docker compose exec trino trino --server https://localhost:8443 --insecure --user analista --password
```

`--insecure` é restrito ao certificado local autogerado. Para uso externo, instalar
certificado confiável e remover essa opção. A senha está no `.env` local.

```sql
SELECT ano, mes, deputado_id, nome_deputado,
       quantidade_lancamentos, valor_liquido
FROM ouro.ouro_camara_deputados.despesas_mensais
WHERE ano = 2025
ORDER BY valor_liquido DESC;
```

Valor líquido é a soma decimal de `vlrLiquido`, incluindo negativos, sem descontar
glosa novamente. Quantidade representa lançamentos, não documentos distintos.
Reprocessamento substitui somente o ano solicitado. Credenciais SQL de consumo
devem negar Prata, DML, DDL e procedures mutáveis; validação real ainda pendente.

## Encerrar

Server e Worker devem permanecer ligados na operação normal. Para uma parada
manual de manutenção, primeiro confirmar runs terminais:

```powershell
docker compose --profile processing stop prefect-worker prefect-server
```

`docker compose stop` para toda a stack preserva dados. Não é necessário remover
volumes para reiniciar; `down -v` remove persistência e não é rotina operacional.
