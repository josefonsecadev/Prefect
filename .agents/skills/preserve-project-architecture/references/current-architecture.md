# Arquitetura atual do projeto

## Sumário

1. [Hierarquia das fontes](#hierarquia-das-fontes)
2. [Capacidade de negócio atual](#capacidade-de-negócio-atual)
3. [Visão sistêmica](#visão-sistêmica)
4. [Organização do código](#organização-do-código)
5. [Fluxos de dados](#fluxos-de-dados)
6. [Infraestrutura e execução](#infraestrutura-e-execução)
7. [Invariantes](#invariantes)
8. [Riscos e lacunas conhecidos](#riscos-e-lacunas-conhecidos)
9. [Validação](#validação)

## Hierarquia das fontes

Usar esta ordem para resolver divergências:

1. código Python, `docker-compose.yml`, `prefect.yaml`, `Dockerfile` e `pyproject.toml` atuais;
2. `README.md`, como explicação do desenho em funcionamento;
3. `PLANO_MELHORIA_ARQUITETURA.md`, como backlog histórico, não como retrato integral do estado atual.

Tratar `.github/agents/prefect.agent.md` como configuração de outra superfície. Ele não substitui esta skill nem os custom agents do Codex.

## Capacidade de negócio atual

O repositório ingere e cura dados públicos da Câmara dos Deputados nos domínios `deputados` e `despesas`. Atualmente entrega Bronze e Prata internas. A camada Ouro, a interface de consulta para clientes, SLOs formais e alta disponibilidade ainda não estão implementados.

Ao avaliar a meta de fornecer dados seguros e sempre disponíveis, distinguir claramente:

- capacidade comprovada no ambiente atual;
- melhoria incremental possível neste repositório;
- requisito de produção que exige infraestrutura, política ou decisão de negócio adicional.

## Visão sistêmica

```text
API/arquivos da Câmara dos Deputados
                |
                v
       flows Prefect 3
                |
                v
      PipeBronze -> MinIO/bronze
                |
                v
       PipePrata -> DuckDB em processo
                |
                v
   catálogo REST Lakekeeper -> Iceberg/MinIO
                |
                v
 PostgreSQL guarda apenas o estado do catálogo
```

A cadeia de herança compartilhada é:

```text
PipeBronze/PipePrata
  -> utils.pipeline.Pipeline
  -> utils.conexoes.Conexoes
  -> utils.config.Config
```

Componentes principais:

| Componente | Responsabilidade atual |
|---|---|
| Prefect Server | API, UI e estados de execução |
| Prefect Worker | deployments e execução no work pool `local` |
| MinIO | objetos Bronze e warehouse Iceberg |
| DuckDB | leitura, transformação e commits Iceberg |
| Lakekeeper | catálogo REST Iceberg |
| PostgreSQL | estado interno do Lakekeeper, não dados analíticos |

## Organização do código

```text
pipelines/camara_deputados/
├── deputados/
│   ├── bronze.py
│   ├── prata.py
│   ├── info.py
│   └── orquestrador.py
└── despesas/
    ├── bronze.py
    ├── prata.py
    ├── info.py
    └── orquestrador.py

utils/
├── camara.py
├── config.py
├── conexoes.py
└── pipeline.py
```

Convenções implementadas:

- definir uma classe `Info` por domínio para nomes e schemas;
- implementar classes `PipeBronze` e `PipePrata` herdando `Pipeline`;
- expor `execute` como método público decorado com `@flow`;
- modelar operações internas orquestradas como `@task`;
- encadear camadas no `orquestrador.py`;
- manter código realmente compartilhado em `utils`;
- usar namespace packages: atualmente não existem arquivos `__init__.py`;
- preservar os entrypoints de `prefect.yaml` e o parâmetro `year`.

Não existe `ouro.py` no estado atual. Criar Ouro somente com contrato de consumo, qualidade, segurança e ownership explícitos.

## Fluxos de dados

### Deputados

```text
GET /api/v2/deputados por página e intervalo anual
  -> bronze/camara_deputados/deputados/ano=YYYY/pagina=N/deputados.json
  -> DuckDB + schema Bronze + ano_referencia
  -> lakehouse.prata.camara_deputados.deputados
```

A tabela Prata é particionada por `ano_referencia`. O reprocessamento substitui somente a partição anual e gera novo snapshot Iceberg.

### Despesas

```text
Ano-YYYY.csv.zip
  -> bronze/camara_deputados/despesas/YYYY/despesas_YYYY.csv.zip
  -> descompactação + DuckDB + schema Prata
  -> lakehouse.prata.camara_deputados.despesas
```

A tabela Prata é particionada por `numAno`, atualmente `VARCHAR`. O reprocessamento substitui somente a partição anual.

### Persistência Iceberg

`utils/pipeline.py` cria namespaces, usa Iceberg format version 2, executa `DELETE` da partição e `INSERT BY NAME` dentro de transação e retorna o snapshot mais recente. `_iceberg_snapshots` e `_read_iceberg` suportam auditoria e time travel.

O warehouse físico usa o bucket `iceberg` e o prefixo `warehouse`. Nunca manipular esses objetos diretamente. Os buckets legados `prata` e `ouro` criados pelo Compose não são o destino das tabelas Iceberg atuais.

## Infraestrutura e execução

`docker-compose.yml` mantém:

- `prefect-server` e o volume `prefect-data`;
- `prefect-worker`, que cria o pool process `local`, define concorrência global 20, registra todos os deployments e inicia o worker;
- `minio` single-node com bind mount local `D:/Dados`;
- jobs `createbuckets`, `lakekeeper-migrate` e `lakekeeper-bootstrap`;
- `lakekeeper` e `lakekeeper-db`;
- rede bridge `prefect-net`.

`prefect.yaml` registra os deployments `camara_despesas` e `camara_deputados_deputados`, ambos sem schedule e com `year: null`. `deployment.py` é uma alternativa manual somente para despesas e não é usado pelo Compose.

O worker usa endpoints Docker (`minio`, `lakekeeper`, `prefect-server`). Execução pelo host usa endpoints `localhost`. Não misturar os dois contextos.

O projeto exige Python `3.14.6`, Poetry, Prefect 3, DuckDB e MinIO. `requests` e `python-dotenv` são importados diretamente, mas ainda chegam apenas como dependências transitivas.

## Invariantes

- Manter Bronze como registro bruto e Prata como dado tratado interno.
- Expor a clientes apenas contratos Ouro deliberadamente projetados.
- Manter secrets fora do Git e falhar sem revelar valores sensíveis.
- Publicar tabelas pelo catálogo e preservar commits/snapshots Iceberg.
- Evitar escrita concorrente não coordenada na mesma tabela/partição.
- Manter reprocessamentos idempotentes por partição.
- Preservar compatibilidade dos entrypoints e parâmetros dos deployments.
- Não ampliar abstrações compartilhadas com regras específicas de apenas um domínio.
- Validar schemas e qualidade antes de tornar dados consumíveis.
- Planejar rollback, time travel ou reprocessamento para mudanças de dados.

## Riscos e lacunas conhecidos

Considerar estes pontos durante a viabilidade; não tentar corrigi-los todos fora do escopo:

- ausência de testes automatizados, lint, type checking e CI;
- ausência de camada Ouro, API/engine de consumo e SLOs;
- deployments sem schedule;
- MinIO, Prefect e Lakekeeper/PostgreSQL single-node, sem backup/restore comprovado;
- ausência de TLS, secret manager e credenciais de menor privilégio;
- ausência de locks por partição apesar da concorrência global 20;
- Bronze sobrescrito sem staging ou manifesto;
- deputados sem timeout/retries e despesas com falha HTTP não explícita;
- ZIP/CSV de despesas mantidos integralmente em memória;
- uma tabela temporária DuckDB por objeto de deputados;
- DuckDB sem limites explícitos de memória, threads ou spill;
- extensões DuckDB instaladas em runtime;
- schemas de despesas inteiramente `VARCHAR`;
- imagens `latest` e versões Prefect divergentes entre runtime e metadado;
- `PLANO_MELHORIA_ARQUITETURA.md` parcialmente anterior à adoção do Iceberg;
- README menciona `.devcontainer`, mas essa configuração não está presente.

## Validação

Selecionar comandos conforme os arquivos afetados:

```powershell
poetry check --lock
git diff --check
```

Validar sintaxe Python sem criar bytecode com AST. Incluir arquivos da raiz, `utils` e `pipelines`.

Quando houver mudança no Compose e o ambiente Docker estiver disponível:

```powershell
docker compose config --quiet
docker compose ps -a
```

Não assumir que pytest, Ruff ou Mypy estão configurados. Se a solicitação introduzir essas ferramentas, registrar a decisão e então executar os comandos adicionados. Executar flows reais somente quando os serviços e credenciais necessários estiverem disponíveis e a ação tiver sido autorizada.
