# TASK-0006 — Validar flows e consolidar RustFS como padrão

## Identificação

- Status: backlog
- Categoria: pipelines
- Tipo: manutencao
- Etiquetas: [rustfs, prefect, duckdb, iceberg, lakekeeper, documentacao, agentes]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário exige manter todo o restante funcional após a migração.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: TASK-0005 concluída e código da TASK-0004 disponível.

## Objetivo e contratos

Comprovar operação ponta a ponta no RustFS, preservar dados antigos e atualizar
documentação e instruções para o novo padrão. Usar Engenharia de Dados para flows
e QA para a avaliação. Não alegar funcionamento completo somente com containers online.
Referências: `AGENTS.md`, `prefect.yaml`, `.vscode/launch.json`, `README.md`,
`.agents/knowledge/planning.md`, skills de arquitetura e engenharia de dados.
Nenhum arquivo de teste, fixture, mock ou script de simulação deve ser criado.

## Etapas

Cada etapa reserva este registro e índice; no máximo cinco arquivos e 5.000 tokens
estimados, incluindo leitura e avaliação. Tempo de execução do flow não é tokens.
Se diagnóstico/correção crescer, registrar a falha e dividir a continuação antes
de ultrapassar o limite. Não testar arquivo por arquivo; executar flows completos.

### E01 — Legislaturas e deputados completos

- Status: backlog.
- Estimativa: 4.000 tokens.
- Arquivos: tarefa e índice; se necessário até três arquivos de correção dentro do escopo.
- Ações: usar ambiente e perfil debug do projeto, confirmando interpretador existente
  e endpoints host/container. Executar orquestrador de legislaturas até Completed;
  depois deputados para recorte explícito compatível com legislaturas publicadas.
- Evidências: comandos/perfis, parâmetros, run IDs, estado terminal, objetos Bronze,
  tabelas Prata, schema, contagens e snapshot. Comprovar objetos no RustFS e ausência
  de dependência do servidor MinIO. Comparar tabelas/snapshots antigos preservados.
- Falhas: registrar erro, causa provável, menor correção e repetir flow completo.
- Resultado: pendente.

### E02 — Despesas e reprocessamento

- Status: backlog; depende de E01.
- Estimativa: 4.000 tokens.
- Arquivos: tarefa e índice; até três correções justificadas, se necessárias.
- Ações: executar despesas completo para ano explícito; repetir os mesmos recortes
  de despesas e deputados, conferindo ausência de duplicatas e preservação dos
  recortes não processados. Conferir snapshots e leitura de versão anterior.
- Evidências: estados terminais, run IDs, contagens por recorte antes/depois,
  snapshots e exemplos de leitura dos dados preservados. Exercitar multipart/range
  pelas operações reais dos flows quando o volume permitir; registrar cobertura real.
- Resultado: pendente.

### E03 — Flow administrativo e retomada da stack

- Status: backlog; depende de E02.
- Estimativa: 4.000 tokens.
- Arquivos: tarefa e índice; até três arquivos para correções dentro do escopo.
- Ações: executar orquestrador de manutenção de particionamento em tabela dedicada
  de validação com dados derivados de recorte existente, preservando tabelas de
  negócio. Usar parâmetros reais do flow, registrar criação e destino da tabela;
  não criar scripts de simulação e não executar migração destrutiva na tabela oficial.
- Conferir contagens, novo particionamento, tabela anterior preservada e leitura.
  Reiniciar serviços sem remover volumes, repetir bootstrap sem duplicar warehouse
  e comprovar leitura persistente. Validar deployments pelo worker além do debug.
- Evidência: run ID terminal sem falha, consultas, persistência e idempotência do bootstrap.
- Resultado: pendente; se ambiente impedir, registrar bloqueio, sem substituir por testes.

### E04 — Documentação e knowledge de arquitetura

- Status: backlog; depende de E03.
- Estimativa: 3.500 tokens.
- Arquivos: `README.md`, `.agents/knowledge/planning.md`, `.agents/knowledge/dev_senior.md`
  quando afetado + controle (até cinco).
- Ações: atualizar stack, diagrama textual, setup, endpoints, variáveis e recuperação;
  converter descrição de migração pendente em arquitetura implementada somente com
  evidências de E01–E03. Explicar SDK MinIO como cliente S3 se permanecer.
- Evidência: instruções coerentes com arquivos efetivamente implantados; sem segredos.
- Resultado: pendente.

### E05 — Skills e encerramento

- Status: backlog; depende de E04.
- Estimativa: 3.000 tokens.
- Arquivos: `.agents/skills/arquiteto-software/SKILL.md`,
  `.agents/skills/engenheiro-dados/SKILL.md`, `AGENTS.md` + controle (cinco).
- Ações: atualizar referências operacionais MinIO para RustFS/S3 quando aplicável,
  mantendo regras das camadas. Conferir referências residuais: históricas e nome
  do SDK podem permanecer; nenhuma configuração padrão deve depender do servidor antigo.
  Se referências de apoio exigirem outros arquivos, dividir em nova etapa.
- Após alterações de código anteriores, executar `graphify update .` conforme AGENTS.md;
  arquivos gerados contam no limite de sua etapa. Se exceder, criar etapa dedicada
  de atualização do grafo antes de encerrar; não inventar grafo atualizado.
- Evidência: QA do conjunto e links; commits por etapa/branch conforme AGENTS.md,
  respeitando autorização de envio. Nenhuma remoção dos dados antigos nesta tarefa.
- Resultado: pendente.

## Critérios de aceite

- [ ] Todos os quatro orquestradores atingiram estado terminal sem falha no novo storage.
- [ ] Reprocessamento sem duplicação, recortes não afetados preservados e snapshots legíveis.
- [ ] Ambiente novo, ambiente migrado, reinicialização e deployments operacionais.
- [ ] RustFS padrão no setup, código e agente; demais serviços e contratos preservados.
- [ ] Evidências verificáveis registradas; impedimentos reais impedem conclusão.

## Retomada e histórico

- Próxima ação: depois da TASK-0005, executar E01.
- Feito: planejamento somente; nenhuma execução alegada.
- Riscos: indisponibilidade das fontes, ambiente debug e compatibilidade exata das versões.
- 2026-11-03 — plano de validação completo registrado a pedido do usuário.
