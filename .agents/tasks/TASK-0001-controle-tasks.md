# TASK-0001 — Criar controle de tarefas do projeto

## Identificação

- Status: concluida
- Categoria: agentes
- Tipo: melhoria
- Etiquetas: [backlog, skills]
- Prioridade: P2
- Complexidade: SIMPLES
- Origem: usuário solicitou controle de tasks com contexto, agrupamento e etapas de até 5 mil tokens.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: nenhuma

## Objetivo e contexto

Guardar demandas dentro do projeto e permitir sua execução e retomada sem depender
do histórico de um chat. Usar Markdown versionado em `.agents`, sem novo serviço.
O limite é de tokens estimados por etapa, não por tarefa inteira.

## Escopo e referências

- Incluído: índice, classificação, ciclo de vida, modelo, skill e integração ao agente.
- Fora do escopo: interface web, automação de contagem de tokens, auditoria técnica e criação de demandas hipotéticas.
- Referências: `AGENTS.md`, `.agents/knowledge/planning.md`, `.agents/knowledge/qa_chato.md`.
- Preservar: serviços, pipelines e regras de validação existentes.
- Limitação: estimativas dependem do contexto e devem ser revistas quando o trabalho crescer.

## Critérios de aceite

- [x] Índice navegável com categoria, prioridade, status e próxima etapa.
- [x] Modelo guarda contexto, dependências, aceite, estimativa, evidências e retomada.
- [x] Limites de 5.000 tokens estimados e cinco arquivos explícitos por etapa.
- [x] Skill registrada no AGENTS.md e fluxo aplicável a demandas futuras.
- [x] Primeiro registro demonstra o uso sem inventar backlog técnico.

## Etapas

### E01 — Instituir controle e revisar instruções

- Status: concluida
- Estimativa: 4.500 tokens.
- Premissas: alteração documental exclusiva do agente; nenhuma implementação de aplicação.
- Dependências: nenhuma.
- Arquivos previstos: `AGENTS.md`, `.agents/skills/gestao-tasks/SKILL.md`, `.agents/tasks/README.md`, `.agents/tasks/TEMPLATE.md`, este registro.
- Ações e entrega: definir convenções, criar os arquivos e integrar o gerenciamento às instruções do agente.
- Validação esperada: validar a skill, revisar os cinco arquivos, conferir links e coerência dos estados e executar `git diff --check`.
- Resultado e evidências obtidas: QA documental aprovado; cinco arquivos revisados, classificação e estados coerentes, referências locais conferidas e `git diff --check` sem erros. Frontmatter da skill revisado manualmente (name e description presentes). O validador `quick_validate.py` não executou por ausência de PyYAML no Python disponível; validação automática da skill permanece como limitação da entrega.
- Branch: `codex/controle-tasks`; commit consultável no histórico Git dessa branch.

## Retomada

- Etapa atual/próxima: nenhuma; controle entregue.
- O que já foi feito: estrutura, regras, modelo e registro inicial criados.
- Próxima ação concreta: registrar a próxima demanda real no modelo com ID TASK-0002.
- Bloqueio e condição de desbloqueio: nenhum.
- Validações pendentes: nenhuma para o aceite documental; execução opcional do validador automático depende de um Python com PyYAML.

## Histórico

| Data | Evento, decisão ou mudança de escopo | Evidência/motivo |
|---|---|---|
| 2026-11-03 | Tarefa registrada e planejada em uma etapa | Pedido do usuário; escopo exclusivo do agente |
| 2026-11-03 | Controle implementado | Cinco arquivos; sem alterações em código de pipelines |
| 2026-11-03 | QA documental aprovado; tarefa concluída | Revisão manual e diff sem erros; validador automático indisponível por falta de PyYAML |
