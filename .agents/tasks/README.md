# Tarefas do projeto

Controle versionado do que precisa ser feito e do contexto necessário para concluir
cada demanda. Cada tarefa fica em `TASK-NNNN-titulo-curto.md`, criada a partir do
[modelo](TEMPLATE.md). O arquivo da tarefa é a fonte de verdade; esta tabela é o índice.

## Índice

| ID | Tarefa | Categoria | Tipo | Prioridade | Status | Próxima etapa |
|---|---|---|---|---|---|---|
| [TASK-0001](TASK-0001-controle-tasks.md) | Criar controle de tarefas do projeto | agentes | melhoria | P2 | concluida | Nenhuma |
| [TASK-0002](TASK-0002-avaliar-storage-s3.md) | Decidir substituto do MinIO | infraestrutura | investigacao | P2 | concluida | RustFS escolhido; seguir TASK-0003 |
| [TASK-0003](TASK-0003-contratos-rustfs.md) | Fechar contratos RustFS + Polaris + Trino | infraestrutura | criacao | P2 | pronta | E01: versões e conexões do ambiente novo |
| [TASK-0004](TASK-0004-codigo-s3-rustfs.md) | Adaptar código para RustFS e Polaris | dados | melhoria | P2 | backlog | E01 após TASK-0003 |
| [TASK-0005](TASK-0005-infra-dados-rustfs.md) | Provisionar RustFS e Polaris do zero | docker | criacao | P2 | backlog | E01 após TASK-0004 |
| [TASK-0006](TASK-0006-validar-documentar-rustfs.md) | Validar flows e consolidar RustFS como padrão | pipelines | manutencao | P2 | backlog | E01 após TASK-0005 |
| [TASK-0007](TASK-0007-acesso-sql-ouro.md) | Planejar engine SQL e catálogo para acesso à Ouro | infraestrutura | investigacao | P2 | pronta | E01: comparar engines e catálogos, incluindo alternativas Apache |

Demandas registradas a partir das solicitações do usuário; classificação secundária no arquivo de cada tarefa.

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
