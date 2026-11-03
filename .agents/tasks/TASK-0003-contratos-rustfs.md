# TASK-0003 — Fechar contratos da migração para RustFS

## Identificação

- Status: pronta
- Categoria: infraestrutura
- Tipo: manutencao
- Etiquetas: [rustfs, s3, lakekeeper, arquitetura]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário escolheu RustFS e pediu tasks para torná-lo armazenamento padrão.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: escolha registrada em TASK-0002; primeira etapa pode iniciar.

## Objetivo, escopo e contratos

Produzir contrato executável para a migração, preservando todo o restante da stack.
Usar Arquitetura de Software. Escopo atual: planejar, sem mover dados ou implantar.
Referências: `.agents/knowledge/planning.md`, `docker-compose.yml`, `.env.example`,
`utils/config.py`, `utils/conexoes.py`, `utils/pipeline.py`, `.vscode/launch.json`.

Contrato aprovado: RustFS substitui apenas o servidor de objetos; Prefect, DuckDB,
Iceberg, Lakekeeper 0.12.1 e PostgreSQL mantêm funções e versões atuais. Preservar
schemas, partições, chaves S3, snapshots, catálogo e reprocessamento. Ambiente local
continua em uma máquina com Docker; produção/HA não faz parte desta migração.
Preservar dados existentes por padrão; não assumir permissão para descartá-los.

Fonte técnica: [API S3 RustFS](https://docs.rustfs.com/en/administration/protocols/s3).
A documentação declara SigV4, path-style, range reads e multipart, mas também
diferenças de compatibilidade; não equivale a validação das versões do projeto.

## Etapas

As estimativas incluem leitura, execução, revisão e atualização do controle.
Em todas as etapas, reservar dois arquivos para tarefa e índice; dividir o restante
antes de exceder 5.000 tokens ou cinco arquivos, incluindo saídas do Graphify.

### E01 — Inventariar contratos e preservação

- Status: pronta
- Estimativa: 3.500 tokens.
- Arquivos: este registro, índice, `.agents/knowledge/planning.md` (três).
- Ações: inventário somente leitura de buckets, objetos, tamanhos, tabelas,
  snapshots e armazenamento disponível; sem registrar segredos. Identificar
  localizações absolutas nos metadados Iceberg e espaço necessário à cópia.
- Contrato proposto: `S3_ENDPOINT` como host:porta, `S3_ACCESS_KEY`, `S3_SECRET_KEY`,
  `S3_REGION=us-east-1`, `S3_USE_SSL=false`, `S3_URL_STYLE=path` para ambiente local;
  dentro da rede `rustfs:9000`, no host `localhost:9000` após corte. HTTPS fora
  do ambiente local deve ser explicitamente configurado, sem desabilitar certificados.
- Aplicação usa variáveis S3; serviço RustFS recebe as variáveis nativas RUSTFS.
  Definir precedência e compatibilidade temporária das antigas MINIO_* sem fallback
  silencioso para o servidor antigo. Manter segredos fora do Git e de logs.
- Evidência esperada: inventário e tabela de contratos preenchidos aqui; se acesso
  não estiver disponível, registrar bloqueio somente das operações dependentes.
- Resultado: pendente.

### E02 — Fixar versão e procedimento operacional

- Status: backlog; depende de E01.
- Estimativa: 4.000 tokens.
- Arquivos: este registro, índice, `.agents/knowledge/planning.md` (três).
- Fixar release estável RustFS e tag/digest verificável, imagem, usuário/permissões,
  diretórios persistentes e healthcheck suportado na versão escolhida. Não usar latest.
- Manter inicialmente o SDK Python `minio` como cliente S3 para evitar mudar todas
  as operações junto com o servidor; isso não exige servidor MinIO. Confirmar que
  as chamadas usadas são S3 padrão. Se houver incompatibilidade, voltar ao planejamento
  e dividir substituição do SDK/dependências em etapa própria antes de implementar.
- Definir bootstrap de buckets usando apenas APIs S3, sem APIs administrativas MinIO.
  Preferir o cliente já disponível na imagem do worker, sem novo serviço permanente.
- Conferir documentação/API da versão Lakekeeper 0.12.1: perfil compatível, acesso
  estático sem STS, atualização de perfil e credenciais do warehouse existente,
  validação de localizações e retorno idempotente. Não inferir suporte da versão atual.
- Definir pausa dos deployments/worker, cópia inicial, sincronização final sem exclusões,
  manifesto verificável, mudança de endpoint e rollback. Após novas escritas no RustFS,
  rollback exige reconciliação dos objetos e do catálogo; não basta religar MinIO.
- Evidência esperada: comandos/APIs, imagem e contratos documentados; etapas seguintes
  refinadas se algum limite ou contrato mudar. Não executar o corte nesta tarefa.
- Resultado: pendente.

## Aceite e retomada

- [ ] Contratos S3, versão e bootstrap definidos com fontes oficiais da versão.
- [ ] Inventário, preservação, corte e rollback definidos, sem exclusões.
- [ ] API do Lakekeeper existente confirmada e tarefas seguintes implementáveis.
- Próxima ação: E01; contrato aprovado não equivale a compatibilidade já validada.
- Riscos: espaço para cópia, permissões no volume Windows/Docker, metadados Iceberg
  com localizações absolutas, perfil persistido antigo, operações multipart/range.
- Histórico: 2026-11-03 — planejamento registrado a pedido do usuário; nenhuma migração executada.
