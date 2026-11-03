# TASK-0004 — Adaptar código para RustFS e Apache Polaris

## Identificação

- Status: concluida
- Categoria: dados
- Tipo: melhoria
- Etiquetas: [rustfs, polaris, s3, duckdb, python, iceberg]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: arquitetura escolhida pelo usuário para ambiente novo.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: TASK-0003 concluída.

## Objetivo e contratos

Usar RustFS para objetos e Polaris como catálogo REST de leitura/escrita do DuckDB.
Preservar regras de negócio, schemas, partições, nomes e parâmetros dos flows,
criando tabelas novas. Não preservar UUIDs, snapshots ou registros de catálogo antigo.
Não manter compatibilidade obrigatória com variáveis MINIO_* ou autenticação Lakekeeper.
Usar Engenharia de Dados; referências: `utils/`, `.env.example`, `.vscode/launch.json`.

## Etapas

Cada etapa inclui este registro e índice (dois arquivos de controle), até cinco
arquivos e 5.000 tokens estimados no total. Sem testes/mocks ou aceite por arquivo;
reprodução completa após integração em TASK-0006.

### E01 — Configuração compartilhada S3 e Polaris

- Status: concluida; estimativa: 3.500 tokens.
- Arquivos: `utils/config.py`, `.env.example` + controle (quatro).
- Implementar contratos S3 e Polaris da TASK-0003, validar endpoint/região/TLS e
  OAuth2 sem expor segredos. Remover exigência de MINIO_*; exemplo aponta para RustFS.
- Evidência: contratos e referências revisados; resultado: pendente.

### E02 — Conexões Python e DuckDB

- Status: concluida; depende de E01; estimativa: 4.000 tokens.
- Arquivos: `utils/conexoes.py`, `utils/pipeline.py` + controle (quatro).
- Configurar cliente S3 e DuckDB com os mesmos parâmetros, renomear abstração
  `_minio` para S3 e ajustar todos os chamadores. Manter SDK somente se compatível.
- Substituir attach/autenticação Lakekeeper por Polaris; tratar aquisição/expiração
  de tokens e acesso S3 conforme contrato. Não usar AUTHORIZATION_TYPE none como padrão.
- Preservar listagem/paginação, multipart, range reads, liberação de conexões e
  exclusões restritas ao recorte. Falhas devem alcançar o flow.
- Evidência: revisão dos chamadores e contratos REST; resultado: pendente.

### E03 — Debug local e endpoints

- Status: concluida; depende de E02; estimativa: 2.500 tokens.
- Arquivos: `.vscode/launch.json`, `.env.example`, `utils/config.py` se necessário + controle (até cinco).
- Ajustar perfis dos flows para endpoints do host e autenticação Polaris; containers
  usam DNS interno. Confirmar interpretador disponível sem inventar caminho debug.
- Evidência: perfis coerentes; flows serão executados completos em TASK-0006.
- Resultado: pendente.

## Aceite e retomada

E01 implementada: Config valida S3, OAuth2, TLS, região e limites DuckDB; exemplo
do host atualizado sem credenciais reais. QA documental/diff aprovado; sem alegar
flow executado. E02/E03 em andamento. Python do host não possui dependências;
Docker Desktop foi iniciado, mas engine ainda não respondeu.

- [x] Acesso S3 e attach Polaris implementados conforme contrato.
- [x] Chamadores e debug consistentes; nenhuma dependência do servidor/catálogo antigo.
- [x] Regras de negócio preservadas; integração pronta para TASK-0005/0006.
- Próxima ação: após TASK-0003, E01. Nenhuma alteração de aplicação executada ainda.
- Histórico: 2026-11-03 — escopo ampliado de armazenamento para RustFS + Polaris;
  descartada exigência de compatibilidade com dados/configurações legadas.

E02/E03 concluídas: `_s3` com região/TLS, DuckDB 128MB/uma thread/temporários em
disco, OAuth2 com timeout e renovação preventiva do secret; chamadores e endpoints
debug migrados. `rg` não encontrou atributos antigos em utils/pipelines. QA do diff
aprovado; cinco arquivos nesta etapa. Critério desta tarefa é entrega de código
pronto para integração; execução e renovação em uso real continuam obrigatórias
na TASK-0006, sem alegar compatibilidade executada. Nenhum teste artificial criado.
