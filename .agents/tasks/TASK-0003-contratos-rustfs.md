# TASK-0003 — Fechar contratos do ambiente novo RustFS + Polaris + Trino

## Identificação

- Status: concluida
- Categoria: infraestrutura
- Tipo: criacao
- Etiquetas: [rustfs, polaris, trino, s3, iceberg, arquitetura]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: escolha explícita do usuário; ambiente novo, sem migrar dados ou catálogos.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: decisões TASK-0002 e TASK-0007 concluídas.

## Objetivo, escopo e contexto

Fechar configuração executável do novo lakehouse antes de implementar. Preservar
Prefect, DuckDB, Iceberg e regras de negócio; substituir MinIO Server e Lakekeeper
por RustFS e Polaris, adicionando Trino para leitura da Ouro. Não inventariar,
copiar, importar ou reconciliar registros antigos. Usar persistência nova.
Referências: `.agents/knowledge/planning.md`, `docker-compose.yml`, `.env.example`,
`utils/config.py`, `utils/conexoes.py`, `utils/pipeline.py`, `.vscode/launch.json`.

## Etapas

Estimativas incluem contexto, execução, revisão e controle. Cada etapa inclui este
registro e índice: até três arquivos adicionais, cinco no total. Dividir antes de
exceder 5.000 tokens; nenhuma implementação ou destruição de dados nesta tarefa.

### E01 — Fixar versões e contratos de conexão

- Status: pronta; estimativa: 4.000 tokens.
- Arquivos: este registro, índice e `.agents/knowledge/planning.md` (três).
- Fixar versões estáveis/imagens/digests RustFS, Polaris e Trino usando documentação
  oficial; verificar compatibilidade de leitura/escrita Iceberg com DuckDB do projeto.
- Definir endpoint S3 interno/host, região, path-style e TLS; variáveis S3_* novas,
  sem obrigação de fallback MINIO_*. Separar credenciais do serviço RustFS das
  identidades de aplicação. Nunca versionar ou registrar valores secretos.
- Definir autenticação OAuth2 Polaris, token endpoint, scope, catálogo/warehouse,
  namespaces Prata/Ouro e como DuckDB e Trino obtêm acesso aos objetos no RustFS.
  Confirmar suporte real de STS/credential vending nas versões; não presumir.
- Definir persistência durável do Polaris (preferir PostgreSQL suportado), volumes
  novos, portas sem conflito, orçamento local de CPU/RAM e prontidão dos serviços.
- SDK Python MinIO pode permanecer como cliente S3 se compatível; não equivale ao
  servidor MinIO. Confirmar operações usadas. Troca de SDK, se necessária, deve ser
  desdobrada em etapa própria com lock/imagem; evitar atualização de dependências alheias.
- Evidência: tabela de versões e contratos preenchida aqui com fontes oficiais.
- Resultado: pendente.

### E02 — Bootstrap e permissões do ambiente novo

- Status: backlog; depende de E01; estimativa: 3.500 tokens.
- Arquivos: este registro, índice e planning (três).
- Definir bootstrap ordenado e idempotente: buckets, backend Polaris, catálogo,
  namespaces, principal escritor, principal leitor e grants. Erros devem propagar;
  HTTP 409 só é aceito após conferir que o recurso corresponde ao contrato novo.
- Escritor DuckDB publica Prata/Ouro; leitor Trino só acessa Ouro e não modifica
  tabelas. Consumidores SQL não recebem credenciais S3 ou privilégios de bootstrap.
- Definir limites/timeouts e autenticação SQL local; separar identidade de
  administração da de consumo. Não prometer HA em uma máquina.
- Documentar ordem de criação do zero e reinicialização sem perda dos dados novos.
  Produto Ouro e regras de negócio serão definidos em TASK-0009, sem bloquear setup.
- Evidência: contrato suficiente para TASK-0004/0005/0008, sem decisões essenciais abertas.
- Resultado: pendente.

## Aceite e retomada

- [x] Versões e contratos RustFS/Polaris/Trino/DuckDB fechados com fontes oficiais.
- [x] Bootstrap, persistência e papéis escritor/leitor definidos.
- [x] Tarefas dependentes implementáveis; nenhum procedimento de migração legado.
- Próxima ação: E01. Validação real do ambiente ocorrerá em TASK-0006/0009.
- Riscos: versões/autenticação incompatíveis, consumo local de recursos e acesso host/container.
- Histórico: 2026-11-03 — plano inicial previa migração MinIO; usuário substituiu
  esse escopo por ambiente novo RustFS + Polaris + Trino. Etapas antigas não foram executadas.

## Contrato fechado e QA — 2026-11-03

E01/E02 concluídas por revisão documental. Imagens: rustfs/rustfs:1.0.4,
apache/polaris:1.8.0, apache/polaris-admin-tool:1.8.0, trinodb/trino:484,
postgres:16.9-alpine; Prefect/Python/DuckDB mantêm dependências do lock existente.
Disponibilidade das imagens e interoperabilidade executável serão verificadas na implantação.

S3_ENDPOINT=rustfs:9000 (host localhost:9000), S3_REGION=us-east-1,
S3_USE_SSL=false apenas rede local, S3_URL_STYLE=path; credenciais S3_ACCESS_KEY e
S3_SECRET_KEY. SDK minio mantido como cliente S3. DuckDB memory_limit=128MB,
threads=1 e temporários em disco configuráveis; não compartilhar conexão entre runs.

ICEBERG_CATALOG_ENDPOINT=http://polaris:8181/api/catalog (host localhost:8181),
ICEBERG_WAREHOUSE=prefect, ICEBERG_CATALOG_NAME=lakehouse; OAuth2 no endpoint
/api/catalog/v1/oauth/tokens, scope PRINCIPAL_ROLE:ALL. Credenciais distintas
POLARIS_CLIENT_ID/SECRET do escritor, POLARIS_READER_CLIENT_ID/SECRET do leitor e
POLARIS_ROOT_CLIENT_ID/SECRET do bootstrap. TOKEN recebido em memória no DuckDB;
renovar antes da expiração ao acessar catálogo. Acesso S3 estático no backend;
credential vending/STS desabilitados nesta entrega, reduzindo dependências.

Persistência relational-jdbc PostgreSQL com volume novo; admin-tool bootstrap do
realm POLARIS antes do servidor, seguido de bootstrap API idempotente de buckets,
catálogo, principal-roles e catalog-roles, namespaces prata_camara_deputados e
ouro_camara_deputados. Escritor gerencia conteúdo; leitor só lista catálogo e lê
Ouro. Trino adiciona regras SQL deny-by-default e autenticação de consumidor.
HTTP local apenas em loopback; exposição externa exige TLS em camada própria.

Trino, Polaris, PostgreSQL e RustFS permanecem ligados. Prefect em profile processing,
concorrência 1; agenda externa dispara batch e desliga somente após runs terminais.
Limites de memória serão explícitos, com meta de 2GB para toda a máquina, não
promessa de capacidade. TASK-0010 mede pico e automatiza janela sem desligar Trino.

Fontes: https://polaris.apache.org/guides/jdbc/ e /guides/trino/;
https://raw.githubusercontent.com/apache/polaris/main/spec/polaris-management-service.yml;
https://docs.rustfs.com/en/administration/protocols/s3;
https://trino.io/docs/current/connector/iceberg.html.
QA: critérios documentais atendidos; flows e RAM não foram validados nesta tarefa.
