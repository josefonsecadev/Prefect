# TASK-0008 — Implantar Trino com Polaris e RustFS

## Identificação

- Status: bloqueada
- Categoria: infraestrutura
- Tipo: criacao
- Etiquetas: [trino, polaris, rustfs, sql, seguranca, ouro, docker]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: escolha explícita Trino + Polaris para acesso SQL à Ouro.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: TASK-0003 e TASK-0005 concluídas; pode avançar antes da TASK-0006,
  mas validação final depende da TASK-0006 e de produto Ouro na TASK-0009.

## Objetivo e contratos

Adicionar serviço Trino ao ambiente novo, conectando ao REST Polaris e aos objetos
Iceberg no RustFS. Consumidor SQL só consulta Ouro; não recebe credenciais S3,
acesso administrativo, DDL/DML ou acesso indireto a Bronze/Prata.
Referências: contrato TASK-0003, `.agents/knowledge/planning.md`, `docker-compose.yml`,
[guia Polaris/Trino](https://polaris.apache.org/guides/trino/).
Começar com coordinator/worker em um nó e recursos explícitos; sem promessa de HA.

## Etapas

Cada etapa reserva tarefa e índice; até três outros arquivos, cinco no total.
Estimativas incluem leitura, configuração, revisão e evidências; dividir antes de 5.000 tokens.

### E01 — Serviço e configuração básica

- Status: backlog; estimativa: 3.500 tokens.
- Arquivos: Compose e até dois arquivos de configuração Trino + controle (cinco).
- Fixar imagem/versão da TASK-0003; configurar JVM, memória, portas, persistência
  apenas quando necessária, logs e healthcheck. Manter serviço interno até autenticação
  e autorização estarem configuradas. Não iniciar acesso público por padrão.
- Evidência: configuração revisada e limites definidos; resultado: pendente.

### E02 — Conector Iceberg REST Polaris

- Status: backlog; depende de E01; estimativa: 4.000 tokens.
- Arquivos: propriedades de catálogo Trino, Compose, `.env.example` + controle (cinco).
- Configurar OAuth2 e principal leitor, namespace Ouro, warehouse e S3 path-style
  RustFS conforme contrato. Segredos em mecanismo externo suportado, sem interpolar
  valores secretos em arquivos versionados ou logs. Confirmar expiração/renovação
  de credenciais e versão do formato Iceberg produzida por DuckDB.
- Evidência: Trino alcança catálogo/storage; tabela de negócio será validada em TASK-0009.
- Resultado: pendente.

### E03 — Autorização SQL e consumidor

- Status: backlog; depende de E02; estimativa: 4.000 tokens.
- Arquivos: configuração de autenticação, regras de acesso e Compose + controle (cinco).
- Separar usuário de consulta e administrador; permitir apenas leitura/metadata
  autorizados da Ouro. Bloquear DDL, DML, procedures de escrita, namespaces internos,
  outros catálogos e caminhos alternativos a arquivos. Read-only global não basta.
- Definir protocolo/cliente SQL suportado, limites de consulta/timeouts, acesso local
  e TLS conforme exposição. Consumidor não conhece credenciais RustFS/Polaris.
- Evidência: regras implementadas; cenários positivos/negativos reais em TASK-0009.
- Resultado: pendente.

## Aceite e retomada

E01–E03 configuradas: Trino 484, OAuth2 leitor, read_only e regras por namespace,
TLS local com certificado próprio, senha PBKDF2, config/segredos gerados fora do
Git. Código aguarda bootstrap/engine; não há validação positiva/negativa alegada.
Dependência TASK-0005 ainda em andamento: implementação antecipada apenas de
configuração para compor setup; status de aceite permanece pendente.

Bloqueio em 2026-11-03: Docker backend falha no socket dockerInference e não
inicializa serviços. Retomar após TASK-0005 operacional: comprovar Trino saudável,
login correto/incorreto, OAuth2 e acesso ao catálogo, antes de concluir a task.
Configuração entregue não equivale a Trino implantado/validado.

- [ ] Trino configurado com principal leitor Polaris e armazenamento RustFS.
- [ ] Autenticação e regras Ouro somente leitura implementadas, sem segredos no Git.
- [ ] Serviço pronto para validação real de TASK-0009, sem alterar flows de transformação.
- Próxima ação: E01 após dependências; nenhum serviço implantado nesta criação de task.
- 2026-11-03 — tarefa criada após aprovação explícita da arquitetura.
