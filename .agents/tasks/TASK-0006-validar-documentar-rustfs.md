# TASK-0006 — Validar flows no ambiente novo RustFS + Polaris

## Identificação

- Status: backlog
- Categoria: pipelines
- Tipo: manutencao
- Etiquetas: [rustfs, polaris, prefect, duckdb, iceberg, documentacao, agentes]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: nova arquitetura aprovada; comprovar funcionamento sem dados/catálogos legados.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: TASK-0005 concluída.

## Objetivo e escopo

Validar publicação nova de Bronze/Prata e manutenção Iceberg com DuckDB, Polaris e
RustFS. Não comparar com dados antigos nem exigir preservação de snapshots legados.
Snapshots criados no ambiente novo devem funcionar normalmente.
Usar Engenharia de Dados, perfil debug e execução completa pelo orquestrador conforme
AGENTS.md. Sem arquivos de testes, fixtures, mocks ou simulações. Consumo Ouro/Trino
é validado em TASK-0009; esta tarefa não encerra a entrega da plataforma inteira.

## Etapas

Cada etapa inclui tarefa e índice; até três outros arquivos, cinco no total.
Estimativas incluem contexto e avaliação, até 5.000 tokens por etapa. Se diagnóstico
ou correção crescer, registrar falha/causa e dividir continuação antes do limite.

### E01 — Legislaturas e deputados

- Status: backlog; estimativa: 4.000 tokens.
- Arquivos: controle e até três correções dentro do escopo.
- Executar legislaturas completo e depois deputados em recorte explícito. Confirmar
  interpretador/perfil real e endpoints corretos do host; não inventar caminho debug.
- Evidência: parâmetros, comandos/perfis, run IDs, Completed, objetos Bronze,
  tabelas Prata, schemas, contagens e snapshots novos no Polaris/RustFS.
- Em falhas, registrar erro/causa provável, aplicar menor correção e repetir flow completo.
- Resultado: pendente.

### E02 — Despesas e idempotência

- Status: backlog; depende de E01; estimativa: 4.000 tokens.
- Arquivos: controle e até três correções.
- Executar despesas completo para ano explícito; repetir mesmos recortes de despesas
  e deputados sem duplicação e sem alterar recortes externos. Ler snapshot anterior
  criado no novo ambiente. Registrar cobertura real de operações multipart/range.
- Evidência: estados terminais, run IDs, contagens por recorte e snapshots.
- Resultado: pendente.

### E03 — Manutenção e persistência

- Status: backlog; depende de E02; estimativa: 4.000 tokens.
- Arquivos: controle e até três correções.
- Executar flow administrativo de particionamento em tabela dedicada com dados reais
  derivados de um recorte; preservar tabelas de negócio. Conferir contagens,
  particionamento e tabela anterior preservada segundo contrato do próprio flow.
- Reiniciar stack sem remover volumes novos; bootstrap não duplica catálogo,
  identidades ou grants. Conferir leitura persistente e execução via deployment/worker.
- Evidência: run ID Completed, consultas, reinicialização e idempotência do bootstrap.
- Resultado: pendente; impedimento de ambiente bloqueia aceite, sem substituir por testes.

### E04 — Documentação do ambiente novo

- Status: backlog; depende de E03; estimativa: 3.000 tokens.
- Arquivos: `README.md`, `.agents/knowledge/planning.md`, `.agents/knowledge/dev_senior.md`
  quando afetado + controle (até cinco).
- Atualizar setup, endpoints, OAuth2, persistência e recuperação do novo ambiente.
  Marcar Trino/Ouro como pendentes enquanto TASK-0008/0009 não concluírem.
  Documentar SDK MinIO como cliente S3 se permanecer, sem confundir com servidor.
- Evidência: instruções refletem configuração implementada e não contêm segredos.
- Resultado: pendente.

### E05 — Instruções e grafo

- Status: backlog; depende de E04; estimativa: 3.000 tokens.
- Arquivos: skills de Arquitetura e Engenharia de Dados, `AGENTS.md` + controle (cinco).
- Atualizar referências MinIO/Lakekeeper operacionais para RustFS/Polaris; preservar
  nomes históricos quando necessário. Se referências auxiliares exigirem mais arquivos,
  dividir etapa. Executar atualização do Graphify após código conforme AGENTS.md;
  saídas contam no limite e exigem etapa própria antes do encerramento se necessário.
- Evidência: QA de instruções, diff e estado real do grafo; resultado: pendente.

## Aceite, retomada e histórico

E04 antecipada para documentar o ambiente configurado e suas limitações reais.
README distingue código entregue de aceites executáveis ainda pendentes. Setup
local disponível; Docker backend falhou ao iniciar e ao reiniciar, e iniciar
com.docker.service foi recusado por permissões. E01–E03 não executadas ainda.

- [ ] Quatro orquestradores completos sem falhas na nova base.
- [ ] Reprocessamento idempotente, snapshots novos e reinicialização comprovados.
- [ ] Documentação/instruções coerentes; pendência de Trino/Ouro explícita.
- Próxima ação: E01 após TASK-0005. Nenhuma execução já realizada.
- 2026-11-03 — escopo atualizado: validação de ambiente novo, sem preservação legada.
