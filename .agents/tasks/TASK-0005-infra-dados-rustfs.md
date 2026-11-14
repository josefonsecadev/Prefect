# TASK-0005 — Provisionar RustFS e Polaris do zero

## Identificação

- Status: bloqueada
- Categoria: docker
- Tipo: criacao
- Etiquetas: [rustfs, polaris, s3, iceberg, postgres, infraestrutura]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário definiu instalação nova sem migração de dados/catálogos.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: TASK-0003 e TASK-0004 concluídas.

## Objetivo e limites

Subir base persistente nova com RustFS e Polaris. Remover MinIO, Lakekeeper e seus
serviços de inicialização do Compose padrão; preservar Prefect, DuckDB e Iceberg.
Reutilizar PostgreSQL como tecnologia somente para backend novo suportado pelo
Polaris; nunca reaproveitar schema/volume de banco Lakekeeper.
Referências: `docker-compose.yml`, `Dockerfile`, `.env.example`, TASK-0003.
Sem inventário/cópia de dados, importação de tabelas, reconciliação de warehouse
legado ou corte/rollback do catálogo antigo. Não é necessário excluir volumes antigos.

## Etapas

Por etapa: este registro + índice e no máximo três outros arquivos; estimativa
inclui leitura e avaliação, até 5.000 tokens. Se precisar de mais helpers, dividir.

### E01 — Serviços e persistência novos

- Status: backlog; estimativa: 4.000 tokens.
- Arquivos: `docker-compose.yml`, `.env.example`, configuração Polaris se necessária + controle (cinco).
- Fixar imagens/versões aprovadas, criar volumes novos RustFS/backend Polaris,
  configurar permissões, portas, DNS, healthchecks de prontidão e dependências.
- Retirar serviços MinIO/Lakekeeper do padrão, sem upgrade paralelo do Prefect.
- Evidência: Compose revisado e topologia coerente; resultado: pendente.

### E02 — Bootstrap de buckets e catálogo

- Status: backlog; depende de E01; estimativa: 4.000 tokens.
- Arquivos: `docker-compose.yml`, helper de bootstrap, `Dockerfile` se necessário + controle (cinco).
- Criar buckets do contrato e inicializar catálogo Polaris em ambiente vazio.
  Persistir estado do catálogo, definir namespace e localização no RustFS sem
  referência a registros antigos. Bootstrap deve ter timeout, retries limitados
  a falhas transitórias e erros visíveis. Conferir idempotência na retomada.
- Evidência: inicialização e reinicialização documentadas, sem afirmar flow validado.
- Resultado: pendente.

### E03 — Identidades e permissões do catálogo

- Status: backlog; depende de E02; estimativa: 3.500 tokens.
- Arquivos: helper de bootstrap, configuração Polaris, `.env.example` + controle (cinco).
- Provisionar escritor de pipelines, leitor de Ouro para Trino e administrador
  de bootstrap separados. Aplicar grants explícitos e acesso S3 previsto no contrato.
  Não registrar segredos. Worker só inicia quando sua configuração estiver pronta.
- Evidência: catálogo novo com papéis/namespace esperados; validação ponta a ponta
  em TASK-0006/0009. Resultado: pendente.

## Aceite e retomada

E01 implementada: Compose com imagens fixas, volumes novos, backend JDBC e profile
processing. Limites de memória iniciais são hipóteses a medir. Engine Docker do
host ainda não responde; nenhuma prontidão ou persistência foi alegada. Bootstrap
API será entregue na próxima etapa; task não concluída antes do aceite executável.

E02/E03 implementadas em `infra/bootstrap.py`: API com timeout e erros sem segredos,
criação idempotente de catálogo/papéis/namespaces e credenciais geradas em runtime.
Perda do arquivo de credenciais exige recuperação explícita; não rotacionar em
silêncio. Prontidão real e grants ainda precisam da execução da stack.

QA adicional: schema PostgreSQL `polaris_schema` criado explicitamente e selecionado
na URL JDBC conforme documentação 1.8.0; montagem de runtime no Trino evita que
Docker crie um diretório no lugar de reader.env antes do bootstrap; shell com LF.
`docker compose config --quiet` passou, sem substituição do aceite de execução.

Timeouts explícitos S3: conexão 5s/leitura 30s, retry limitado a falhas transitórias.

## Bloqueio de ambiente e retomada — 2026-11-03

`docker compose up --build -d` não respondeu em 30s (TimeoutExpired). Docker Desktop
4.80.0 não iniciou engine Linux: log do backend relata `initializing Inference
manager` / `dockerInference` / `The file cannot be accessed by the system`.
Reinício pelo CLI também expirou. Start-Service com.docker.service foi recusado
por permissões. Tentativa de remover apenas socket temporário com Docker parado
foi rejeitada pela revisão automática de segurança (`blocked by policy`), sem
detalhamento; não contornada. Nenhum volume foi removido.

Desbloqueio: reparar/iniciar Docker Desktop até `docker info` responder. Depois
executar `docker compose up --build -d`, conferir imagens, permissões, bootstrap
e reinicialização; corrigir falhas reais antes de marcar os critérios acima.
Configuração e implementação foram commitadas; task continua pendente de aceite.

- [ ] RustFS e Polaris padrão, com persistência e inicialização idempotente.
- [ ] Ambiente nasce vazio sem depender de MinIO, Lakekeeper ou seus dados.
- [ ] Credenciais separadas e dependências corretas; pronto para executar flows.
- Próxima ação: após dependências, E01. Nenhum serviço/volume alterado nesta revisão.
- Histórico: 2026-11-03 — usuário dispensou migração e preservação de dados antigos;
  planejamento de cópia/corte substituído por provisionamento limpo.
