# Tarefas do projeto

Controle versionado do que precisa ser feito e do contexto necessário para concluir
cada demanda. Cada tarefa fica em `TASK-NNNN-titulo-curto.md`, criada a partir do
[modelo](TEMPLATE.md). O arquivo da tarefa é a fonte de verdade; esta tabela é o índice.

## Índice

| ID | Tarefa | Categoria | Tipo | Prioridade | Status | Próxima etapa |
|---|---|---|---|---|---|---|
| [TASK-0001](TASK-0001-controle-tasks.md) | Criar controle de tarefas do projeto | agentes | melhoria | P2 | concluida | Nenhuma |
| [TASK-0002](TASK-0002-avaliar-storage-s3.md) | Decidir substituto do MinIO | infraestrutura | investigacao | P2 | concluida | RustFS escolhido; seguir TASK-0003 |
| [TASK-0003](TASK-0003-contratos-rustfs.md) | Fechar contratos RustFS + Polaris + Trino | infraestrutura | criacao | P2 | concluida | Contrato fechado; executar TASK-0004 |
| [TASK-0004](TASK-0004-codigo-s3-rustfs.md) | Adaptar código para RustFS e Polaris | dados | melhoria | P2 | concluida | Código entregue; validar em TASK-0006 |
| [TASK-0005](TASK-0005-infra-dados-rustfs.md) | Provisionar RustFS e Polaris do zero | docker | criacao | P2 | bloqueada | Reparar engine Docker; validar bootstrap entregue |
| [TASK-0006](TASK-0006-validar-documentar-rustfs.md) | Validar flows no ambiente novo RustFS + Polaris | pipelines | manutencao | P2 | bloqueada | Docker ativo; executar flows reais e atualizar grafo |
| [TASK-0007](TASK-0007-acesso-sql-ouro.md) | Escolher arquitetura de acesso SQL à Ouro | infraestrutura | investigacao | P2 | concluida | Trino + Polaris aprovados; execução nas tasks |
| [TASK-0008](TASK-0008-implantar-trino.md) | Implantar Trino com Polaris e RustFS | infraestrutura | criacao | P2 | bloqueada | Docker ativo; validar serviço e autenticação |
| [TASK-0009](TASK-0009-produto-ouro-consumo.md) | Publicar Ouro e validar consumo pelo Trino | dados | criacao | P2 | bloqueada | Docker ativo; validar despesas mensais implementadas |
| [TASK-0010](TASK-0010-janela-processamento.md) | Automatizar Prefect e medir orçamento de 2GB | orquestracao | criacao | P2 | bloqueada | Janela abandonada na TASK-0023; replanejar medição em operação contínua |
| [TASK-0011](TASK-0011-diagnostico-docker-recursos.md) | Diagnosticar stack Docker e recursos | observabilidade | investigacao | P2 | concluida | Diagnóstico entregue; stack instável; seguir TASK-0012 |
| [TASK-0012](TASK-0012-capacidade-wsl.md) | Ajustar capacidade do WSL | infraestrutura | melhoria | P1 | em_revisao | Interfaces HTTP 200; corrigir deployment Worker e validar carga |
| [TASK-0013](TASK-0013-reduzir-imagem-python.md) | Reduzir imagem Python | docker | melhoria | P2 | backlog | Medir camadas da imagem nova |
| [TASK-0014](TASK-0014-retencao-docker.md) | Definir retenção de imagens e cache | docker | manutencao | P2 | backlog | Classificar candidatos sem apagar dados |
| [TASK-0015](TASK-0015-base-testes-carga.md) | Criar executor e métricas de carga | observabilidade | criacao | P2 | backlog | Definir quatro níveis, limites e contrato de coleta |
| [TASK-0016](TASK-0016-carga-individual-servicos.md) | Testar carga individual por serviço | observabilidade | criacao | P2 | backlog | Após 0015, implementar adaptadores e baselines |
| [TASK-0017](TASK-0017-carga-conjunta-lakehouse.md) | Testar carga conjunta e recuperação | observabilidade | criacao | P2 | backlog | Após baselines, executar misturas graduais |
| [TASK-0018](TASK-0018-relatorio-capacidade-producao.md) | Analisar capacidade para produção | observabilidade | investigacao | P2 | backlog | Consolidar curvas, limites e recomendações |
| [TASK-0019](TASK-0019-flows-parquet-rustfs.md) | Executar flows com Parquet no RustFS | pipelines | melhoria | P1 | bloqueada | Resolver API Legislaturas 504 e regra Ouro das lideranças |
| [TASK-0020](TASK-0020-economia-tokens-agente.md) | Reduzir contexto e repetição do agente | agentes | melhoria | P1 | concluida | Aplicar fluxo econômico nas próximas demandas |
| [TASK-0021](TASK-0021-acesso-ui-prefect.md) | Corrigir conexão da interface Prefect | docker | correcao | P1 | concluida | Recarregar interface no navegador |
| [TASK-0022](TASK-0022-env-fixo.md) | Adotar .env fixo e remover gerador | infraestrutura | melhoria | P2 | concluida | Nenhuma |
| [TASK-0023](TASK-0023-remover-batch.md) | Remover execução por janela | orquestracao | melhoria | P2 | concluida | Nenhuma |
| [TASK-0024](TASK-0024-simplificar-inicializacao.md) | Separar instalação e operação | infraestrutura | melhoria | P2 | concluida | Operação contínua; instalação nova não reproduzida |
| [TASK-0025](TASK-0025-nessie-clickhouse.md) | Trocar Polaris/Trino por Nessie/ClickHouse | infraestrutura | melhoria | P1 | bloqueada | Resolver leitura de tabelas por nome no ClickHouse para o usuário analista |
| [TASK-0026](TASK-0026-tutorial-criar-flow.md) | Documentar criação de um flow novo | documentacao | melhoria | P2 | concluida | Nenhuma |

Demandas registradas a partir das solicitações do usuário; classificação secundária no arquivo de cada tarefa.

Arquitetura alvo atual: **Prefect + DuckDB + RustFS + Iceberg/Nessie + ClickHouse**.
As tasks 0003 a 0009 registram decisões e implementações históricas de Polaris/Trino;
foram substituídas pela TASK-0025. O flow Iceberg publica com Nessie, mas a leitura
via `DataLakeCatalog` ClickHouse/RustFS permanece bloqueada por incompatibilidade
confirmada no ClickHouse 26.8.36.3. Containers antigos foram parados, volumes mantidos.

## Classificação

Escolha uma categoria principal pelo resultado da tarefa. Componentes secundários
ficam em etiquetas; assim uma nova pipeline que altera o Compose continua agrupada
em `pipelines`, com etiqueta `docker`.

| Categoria | Agrupamento |
|---|---|
| pipelines | Criação, correção e evolução de flows de domínio |
| dados | Schemas, qualidade, modelagem, tabelas e migrações de dados |
| orquestracao | Deployments, agendas, pools e operação do Prefect |
| infraestrutura | Serviços, rede, armazenamento e disponibilidade |
| docker | Imagens, Compose, containers e ambiente de execução |
| backend | APIs e serviços de aplicação |
| frontend | Interfaces e experiência de uso |
| observabilidade | Logs, métricas, alertas e diagnóstico operacional |
| seguranca | Credenciais, permissões e proteção de dados |
| documentacao | Guias e documentação do projeto |
| agentes | AGENTS.md, skills, conhecimentos e controle do agente |

Tipos: `criacao`, `melhoria`, `correcao`, `manutencao`, `investigacao`.
Etiquetas são livres, preferencialmente reutilizadas: `prefect`, `minio`,
`iceberg`, `lakekeeper`, `duckdb`, `docker`, `camara-deputados`, `bronze`, `prata`, `ouro`.

Prioridades: **P0** incidente crítico; **P1** alto impacto ou bloqueio de entrega;
**P2** trabalho normal; **P3** melhoria de baixa urgência. Sem indicação de urgência,
use P2 e justifique mudanças de prioridade no histórico.

## Ciclo de vida

`backlog → pronta → em_execucao → em_revisao → concluida`

- `backlog`: demanda registrada, ainda a detalhar ou priorizar.
- `pronta`: próxima etapa definida, estimada e sem dependências pendentes.
- `em_execucao`: etapa em andamento; registre qual.
- `em_revisao`: implementação pronta, aguardando avaliação e validações finais.
- `bloqueada`: falta informação, dependência ou ambiente; registre como desbloquear.
- `concluida`: todos os critérios de aceite e validações atendidos.
- `cancelada`: trabalho encerrado sem entrega; preserve motivo e histórico.

Uma revisão reprovada retorna a `em_execucao`; bloqueios podem ocorrer em qualquer
estado aberto e retornam ao estado cabível após resolução. Etapas usam os mesmos
estados. Tarefas canceladas ou concluídas permanecem no índice.

## Etapas e retomada

Cada etapa deve entregar algo verificável, estimar **até 5.000 tokens** e alterar
**até cinco arquivos**, contando o próprio registro e o índice quando modificados.
O total da tarefa pode ultrapassar 5.000 tokens somando várias etapas. Estime o
trabalho completo da etapa, não apenas o tamanho do código produzido. Divida o
restante se novas descobertas invalidarem a estimativa.

Registre dependências por ID e, quando necessário, por etapa (`TASK-0002/E01`).
Não inicie etapas dependentes antes de sua entrega. Não registre segredos ou
logs sensíveis nos arquivos de tarefas.

Para pedir trabalho: “registre uma tarefa para ...”, “liste as pendências de
infraestrutura” ou “retome a TASK-0002”. Ao encerrar uma sessão, mantenha o próximo
passo específico e o resumo de execução atualizados no arquivo da tarefa.
