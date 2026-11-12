---
name: gestao-tasks
description: Registrar, priorizar, dividir e retomar alterações do projeto em .agents/tasks.
---

# Gestão de tasks

1. Consulte o índice `.agents/tasks/README.md` e somente registros relacionados.
   Perguntas informativas e entrega Git sem alteração de escopo não criam task.
2. Antes de alterar, reutilize task pertinente ou atribua próximo TASK-NNNN livre,
   conferindo arquivos/índice. Baseie-se no TEMPLATE.md proporcionalmente: origem,
   objetivo, categoria/tipo/prioridade, escopo, dependências, aceite e próximo passo.
   Não transformar sugestões em implementação autorizada.
3. Etapas até cinco arquivos e 5.000 tokens estimados, incluindo controle; dividir
   somente quando necessário. Estimativa é teto de planejamento, não meta de uso.
   Task simples pode ter uma etapa curta; não duplicar plano em vários documentos.
4. Uma task em execução por agente e uma branch por demanda. Atualize evidências em
   marcos ou mudança relevante: arquivos, comando/run ID, resultado, causa e retomada.
   Não registrar cada comando, saída completa ou repetir todo histórico.
5. Status: backlog (a detalhar), pronta (sem decisão essencial pendente), em_execucao,
   em_revisao, bloqueada, concluida ou cancelada. Bloqueio inclui condição para retomar;
   concluir só com aceite comprovado. Flows seguem AGENTS.md; agente exclusivo exige
   apenas planning/QA. Preserve histórico e não invente backlog.
6. Atualize índice junto de título/classificação/status/próxima etapa; a task é a fonte
   de verdade. Ao retomar, confira Git e evidências atuais. Encerramento: resumo curto
   com estado, arquivos/run IDs e próximo passo suficiente para outro chat.

Registro não autoriza push ou ações externas. Commits por entrega coerente, sem
branch/commit por microatualização. AGENTS.md concentra a política comum de leitura,
logs, acompanhamento e validação; não recarregar guias já disponíveis no contexto.
