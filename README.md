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
./.venv/Scripts/python.exe -m infra.init_env
docker compose up --build -d
docker compose ps -a
```

`infra.init_env` cria `.env` com segredos aleatórios e não os imprime. Se já existir
um `.env` de outra instalação, `--replace` guarda uma cópia local em `.prefect/runtime`
antes de gerar o novo. Nunca versionar `.env`, runtime, certificados ou chaves.

Ordem de inicialização: RustFS e PostgreSQL, bootstrap JDBC Polaris, Polaris,
`lakehouse-setup`, Trino. Serviços de bootstrap devem encerrar com código zero.
Catálogo/roles/namespaces são idempotentes. Perda dos arquivos de credenciais do
runtime exige recuperação ou rotação explícita; não são recriados silenciosamente.

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
| Prefect Server | Janela de processamento | http://localhost:4200 |
| Prefect Worker | Janela de processamento | Sem porta publicada |

Volumes nomeados novos: rustfs-data, polaris-db-data e prefect-data. Os arquivos
`.prefect/runtime/writer.env`, `reader.env` e `trino/` também são persistência
operacional: guardar com proteção adequada junto com backup do catálogo/storage.

## Executar e depurar flows

```powershell
docker compose --profile processing up -d prefect-worker
```

As dependências iniciam o Server e aguardam bootstrap. No VS Code, usar os perfis
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

## Janela automática do Prefect

Deixe a base e o Trino ligados e Prefect desligado antes de iniciar:

```powershell
./.venv/Scripts/python.exe -m infra.batch --year 2025
```

O batch recusa duplicação por trava local, inicia Prefect, executa legislaturas
como pré-requisito e depois os dois produtos (deputados e despesas), em sequência.
Na janela automática, o executor usa `compose run --rm` com a imagem do worker,
sem manter outro processo de polling simultâneo. Deployments pela interface usam
o serviço worker tradicional iniciado manualmente.
Só para Worker/Server após confirmar ausência de runs ativos. Em dúvida, deixa
Prefect ligado e retorna falha. Trino e sua base permanecem ativos.

Agendador de Tarefas do Windows: chamar o Python absoluto da `.venv`, argumentos
`-m infra.batch --year ANO`, diretório inicial igual à raiz do repositório e opção
de não iniciar outra instância. Em Linux, o mesmo comando pode ser chamado por
systemd timer/cron. Nenhum horário foi cadastrado automaticamente.

Amostras dos containers ficam em `.prefect/runtime/memory.jsonl`. Também medir
memória total do host, OOM e pico real durante consultas/flows: somar limites de
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

Para parar apenas processamento, primeiro confirmar runs terminais:

```powershell
docker compose --profile processing stop prefect-worker prefect-server
```

`docker compose stop` para toda a stack preserva dados. Não é necessário remover
volumes para reiniciar; `down -v` remove persistência e não é rotina operacional.
