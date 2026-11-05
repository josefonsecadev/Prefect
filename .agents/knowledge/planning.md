# A Arquitetura
Decisão de operação (2026-11-05, TASK-0024): provisionamento de buckets, catálogo e
permissões é uma ação explícita de instalação. Subir serviços não deve executar o
provisionador da aplicação. Configurações de infraestrutura ficam em infra; segredos
locais são fixos em .env ignorado.

Decisão de arquitetura (2026-11-05, TASK-0025): manter RustFS, Iceberg, DuckDB e
Prefect; substituir Polaris/PostgreSQL por Project Nessie como catálogo Iceberg REST
e Trino por ClickHouse como endpoint SQL. A validação da integração Nessie/S3 e do
catálogo Iceberg no ClickHouse é critério de aceite desta task.

Fonte de verdade para planejar a arquitetura do projeto e definir os contratos que serão entregues para execução.

## O que é o projeto

O projeto coleta, transforma e disponibiliza dados com valor de negócio para diferentes consumidores, principalmente ferramentas de Business Intelligence, aplicações analíticas e APIs.

O planejamento é responsável por decidir como cada demanda se integra a essa plataforma. Antes de enviar uma etapa para desenvolvimento, deve definir arquitetura, escopo, contratos, riscos, critérios de aceite e validações esperadas.

## Estrutura do projeto

| Componente | Responsabilidade |
|---|---|
| Prefect Server | API, interface web, agendamentos e estado das execuções |
| Prefect Worker | Execução dos flows e tasks |
| DuckDB | Leitura, transformação e publicação dos dados |
| RustFS | Armazenamento S3 dos arquivos brutos e das tabelas Iceberg |
| Apache Iceberg | Formato de tabela, schema, partições, snapshots e transações |
| Project Nessie | Catálogo REST Iceberg com persistência local RocksDB |
| ClickHouse | Endpoint SQL para consultar tabelas Iceberg |

O catálogo Nessie não recebe regras de negócio dos pipelines. ClickHouse lê Iceberg
diretamente por `icebergS3()` quando recebe o path da tabela, mas essa chamada exige
usuário administrativo no perfil atual e não descobre tabelas via Nessie. A integração
de consumo por nome segue bloqueada; consulte TASK-0025 antes de considerar o acesso
SQL para analistas pronto.

## Arquitetura de dados

### Validação incremental aprovada em 2026-11-04: Parquet direto no RustFS

Por solicitação do usuário, TASK-0019 entrega execução dos flows de dados sem
catálogo/Trino nesta fase. Modo explícito `PIPELINE_STORAGE_FORMAT=parquet` publica
Prata/Ouro tipadas como arquivos Parquet no RustFS, mantendo o modo `iceberg`
existente como default. Bronze mantém o formato recebido/contrato já implementado.
Leituras entre flows usam esses arquivos no mesmo modo. Caminho:
`<camada>/<projeto>/<pipeline>/<tabela>/<coluna>=<recorte>/data.parquet`, sem recorte
quando tabela integral. Escrita serial e substituição de uma chave por recorte,
sem remoção antecipada; validar Parquet/schema/contagem e readback remoto.
Não há garantia transacional multiobjeto, catálogo ou snapshots neste modo.
Legislaturas e deputados: Bronze/Prata; despesas: Bronze/Prata/Ouro. Manutenção
Iceberg permanece fora desta validação. Esta entrega não conclui aceites Iceberg,
permissões SQL ou Trino e não substitui a arquitetura alvo abaixo.

### Decisão histórica, substituída pela TASK-0025: RustFS, Polaris e Trino

Em 2026-11-03, o usuário escolheu RustFS como armazenamento, Apache Polaris como
catálogo e Trino como engine SQL de acesso à Ouro. Essa decisão foi substituída em
2026-11-05 pelo uso de Nessie e ClickHouse. O ambiente será provisionado
do zero quanto a dados, catálogos, registros de tabelas, usuários e volumes novos.
Não há requisito de copiar ou preservar dados e catálogos anteriores na solução.
Essa dispensa não exige apagar volumes antigos para executar o planejamento.

- Planejamento e execução rastreados em TASK-0003 a TASK-0009, em `.agents/tasks/`.
- Preservar Prefect, DuckDB, Iceberg e regras de negócio dos pipelines existentes.
  Remover MinIO Server, Lakekeeper e seus bootstraps do caminho padrão; não construir
  reconciliação, importação ou compatibilidade de catálogo antigo.
- Manter a topologia local de uma máquina em Docker; não introduzir cluster ou
  promessas de alta disponibilidade que essa topologia não oferece.
- RustFS e Polaris terão persistência própria e vazia. Não montar diretório interno
  MinIO no RustFS nem reaproveitar banco Lakekeeper como backend Polaris.
- Usar configuração S3 explícita (endpoint, credenciais, região, TLS e path-style),
  padrão apontando para RustFS; variáveis antigas MINIO_* não são contrato obrigatório.
- DuckDB escreve Prata/Ouro pelo REST Polaris; Trino consulta as tabelas pelo mesmo
  catálogo e lê os objetos no RustFS. Consumidores recebem identidade SQL sem
  credenciais S3 e só acessam Ouro. Separar escritor, leitor e bootstrap administrativo.
- Provisionamento explícito cria buckets, catálogo, namespaces, identidades e
  permissões na instalação; é idempotente e não participa do startup diário.
- TASK-0003 fixa versões, autenticação e contratos; TASK-0004 adapta código;
  TASK-0005 provisiona a base; TASK-0006 valida flows; TASK-0007 registra decisão;
  TASK-0008 entrega Trino; TASK-0009 define produto Ouro e valida consumo completo.
- Só concluir com execução real de flows completos, reprocessamento sem duplicação,
  persistência após reinicialização e consultas/permissões SQL comprovadas.

O projeto segue a arquitetura medalhão:

```text
Fonte de dados
    |
    v
Bronze no RustFS
    |  arquivos JSON, CSV e ZIP recebidos das fontes
    v
Prata no Iceberg
    |  dados tratados, tipados, particionados e versionados
    v
Ouro no Iceberg
       tabelas agregadas destinadas a APIs, dashboards e usuários finais
    |
    v
ClickHouse (SQL sobre Iceberg; integração em validação na TASK-0025)
```

## Organização do código

| Caminho | Responsabilidade arquitetural |
|---|---|
| `pipelines/<mini_projeto>/<flow>/orquestrador.py` | Compor o flow completo e definir a ordem das camadas |
| `pipelines/<mini_projeto>/<flow>/bronze.py` | Extrair dados da origem e persistir o conteúdo bruto |
| `pipelines/<mini_projeto>/<flow>/prata.py` | Limpar, tipar, validar e publicar dados tratados |
| `pipelines/<mini_projeto>/<flow>/ouro.py` | Criar produtos agregados orientados ao consumo, quando necessário |
| `pipelines/<mini_projeto>/<flow>/info.py` | Centralizar metadados, nomes e schemas específicos do pipeline |
| `utils/` | Concentrar capacidades reutilizadas por dois ou mais pipelines |
| `prefect.yaml` | Declarar deployments, entrypoints, parâmetros e work pools |
| `docker-compose.yml` | Definir os serviços e as dependências do ambiente |

Funções específicas de uma demanda permanecem em seu pipeline. Uma implementação só deve ir para `utils/` quando representar uma capacidade comum a mais de um flow.

## Decisões arquiteturais obrigatórias

Todo planejamento deve definir, quando aplicável:

1. fonte e forma de acesso aos dados;
2. domínio e pipeline responsáveis;
3. camadas afetadas e responsabilidade de cada uma;
4. contratos de entrada e saída;
5. schemas, formatos e regras de qualidade;
6. estratégia de particionamento e recorte de reprocessamento;
7. comportamento idempotente da escrita;
8. parâmetros do flow e limites de concorrência;
9. estratégia de falha, retry e timeout;
10. logs e evidências operacionais necessárias;
11. impacto em infraestrutura, configuração e segurança;
12. critérios de aceite e validações da implementação.

Uma decisão arquitetural não pode ser transferida implicitamente ao desenvolvimento. Se uma dessas definições afetar a solução, ela deve estar explícita antes da execução.

## Regras por camada

### Bronze

- Preserva o conteúdo e o formato recebidos da origem sempre que possível.
- Organiza objetos por projeto, pipeline e recorte lógico, como data ou ano.
- Valida a resposta da origem antes da persistência.
- Não sobrescreve dados fora do recorte solicitado.

### Prata

- Consome a Bronze e aplica schema, tipos, nomes e regras de qualidade explícitos.
- Trata mudanças de contrato e dados inválidos como falhas identificáveis.
- Usa particionamento alinhado aos filtros e reprocessamentos frequentes.
- Publica no Iceberg de forma transacional e versionada.

### Ouro

- Primeiro produto planejado: `ouro_camara_deputados.despesas_mensais`, granularidade
  deputado (`ideCadastro`), ano e mês; soma decimal de `vlrLiquido`, incluindo
  negativos, sem novo desconto de glosa; contagem de lançamentos. Reprocessar
  somente o ano solicitado. Contrato detalhado e aceite na TASK-0009.

- Existe apenas quando há uma necessidade de consumo definida.
- Mantém métricas e regras de negócio explícitas e testáveis.
- Consome preferencialmente a Prata e não acessa diretamente a fonte ou a Bronze sem justificativa arquitetural.

## Orquestração

- O flow completo da demanda é composto em `orquestrador.py`.
- Parâmetros de execução entram pelo orquestrador e devem ser resolvidos uma única vez.
- Cada camada expõe uma entrada clara e tipada.
- Tasks representam unidades de trabalho que precisam de observabilidade, retry, timeout ou estado operacional próprio.
- Funções puras e auxiliares pequenas não precisam se tornar tasks.
- Falhas de tasks devem alcançar o estado do flow; exceções não podem ser silenciadas para manter uma execução aparentemente bem-sucedida.

## Dados, reprocessamento e disponibilidade

- Reexecutar o mesmo recorte não pode duplicar dados.
- Escritas devem substituir somente a partição lógica processada quando o contrato exigir reprocessamento.
- Schemas, nomes de tabelas, partições e formatos são contratos explícitos.
- Operações externas precisam de timeout.
- Retry é reservado a falhas transitórias e deve ter limite definido.
- Erros de schema, contrato ou regra de negócio falham imediatamente.
- Alterações de concorrência, particionamento ou recursos exigem justificativa baseada em volume, latência, disponibilidade ou custo.
- Healthchecks devem representar prontidão real do serviço.

### Manutenção de particionamento Iceberg

- Alterações de particionamento de tabelas Iceberg devem ser executadas por flow administrativo dedicado, fora dos flows de domínio.
- O procedimento padrão cria uma nova tabela com o novo particionamento, copia todos os dados da tabela anterior, valida a contagem de registros e só então promove a nova tabela para o nome oficial.
- A tabela anterior não deve ser apagada durante a migração. Ela deve ser renomeada com sufixo de desativação e marcada com propriedades Iceberg de depreciação, preservando os dados para auditoria e rollback operacional.
- Tabelas desativadas permanecem no mesmo warehouse Iceberg. Criar outro bucket ou warehouse para desativação exige nova decisão arquitetural, pois altera infraestrutura, catálogo e operação.

## Configuração e segurança

- Configurações variáveis pertencem a variáveis de ambiente.
- Valores seguros de exemplo pertencem ao `.env.example`.
- Credenciais e tokens não podem ser versionados, registrados em logs ou incluídos em mensagens de erro.
- Conexões compartilhadas devem permanecer centralizadas nas abstrações comuns definidas pelo projeto.
- Identificadores e valores usados em SQL devem ser validados ou parametrizados.
- Novas dependências precisam de justificativa arquitetural e devem ser refletidas no arquivo de lock e na imagem Docker.

## Tecnologias utilizadas

- Python é a linguagem principal para coleta e transformação.
- `requests` é usado para APIs, DuckDB para leitura e transformação e Selenium para fontes web que realmente dependam de navegador.
- RustFS armazena objetos do datalake; Nessie mantém o catálogo REST Iceberg e ClickHouse oferece acesso SQL à Ouro.
- Apache Iceberg fornece catálogo lógico de tabelas, schemas, snapshots, particionamento e transações.
- Prefect define flows, tasks, deployments, estados e agendamentos.
- Todos os serviços de produção devem ser dockerizados.
- O ambiente local deve reproduzir a topologia e o comportamento de produção para permitir validações confiáveis.

## INFORMAÇÕES INDISPENSÁVEIS PARA PLANEJAMENTO

1. Leia `AGENTS.md` e inspecione a implementação atual antes de propor alterações.
2. Identifique o objetivo do usuário, os consumidores afetados e o resultado observável esperado.
3. Confirme volume, frequência, recorte de reprocessamento e requisitos de disponibilidade.
4. Verifique se a solução respeita as responsabilidades e os contratos definidos neste documento.
5. Divida a solução em etapas que alterem no máximo cinco arquivos cada.
6. Entregue ao desenvolvimento todas as entradas obrigatórias definidas neste knowledge.

## PASSOS PARA SEGUIR 

AO RECEBER A DEMANDA, DEFINA A ARQUITETURA E DIVIDA A EXECUÇÃO EM ETAPAS QUE LEVEM NO MÁXIMO UM MINUTO PARA SEREM ARQUITETADAS. CASO A SOLICITAÇÃO NÃO PERMITA ESSA DECOMPOSIÇÃO, INTERROMPA O PROCESSAMENTO E SOLICITE QUE A DEMANDA SEJA QUEBRADA.

A arquitetura pode evoluir quando a mudança simplificar o sistema ou melhorar comprovadamente a qualidade dos dados, o tempo de resposta, a disponibilidade ou o custo operacional. A decisão e seus impactos devem ser registrados neste documento antes da implementação.

