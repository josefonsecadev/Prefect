---
name: gestao-tasks
description: Registrar, classificar, priorizar, decompor e acompanhar tarefas de alteração do projeto em .agents/tasks, com contexto para execução e retomada entre chats.
---

# Gestão de tasks

Use `.agents/tasks/README.md` como índice e regras do controle. Use
`.agents/tasks/TEMPLATE.md` para criar o registro completo de uma demanda.

1. Consulte o índice e procure uma tarefa existente para evitar duplicação. Leia
   somente os registros relevantes à demanda; não carregue todo o backlog.
2. Atribua o próximo ID sequencial livre `TASK-NNNN`, sem reutilizar IDs de
   tarefas canceladas. Confira arquivos e índice antes de escolher o ID.
3. Registre a origem, o objetivo observável, contexto confirmado, escopo,
   referências, categoria, tipo, prioridade, dependências e critérios de aceite.
   Não invente backlog ou trate sugestões como demandas autorizadas.
4. Divida o trabalho em etapas com entrega verificável, até cinco arquivos e
   estimativa de até 5.000 tokens cada. Inclua leitura, implementação, avaliação
   e atualização do controle na estimativa; deixe margem para imprevistos.
   Estimativas não são medição nem garantia de consumo real. Registre as premissas.
5. Antes de executar, confira dependências e informações obrigatórias. Uma tarefa
   só fica `pronta` quando permite iniciar a próxima etapa sem decisões essenciais
   pendentes. Use as skills técnicas aplicáveis; o registro não substitui o planejamento.
6. Execute uma etapa por vez. Atualize o status e mantenha registro suficiente
   para retomar: resultado, arquivos, evidências, decisões e próximo passo exato.
   Se o escopo crescer além do limite, registre o realizado e divida o restante
   em novas etapas antes de continuar. Não dependa de gastar os 5.000 tokens.
7. Para bloqueios, registre causa, impacto, ação necessária e condição de retomada.
   Para novas demandas descobertas fora do escopo, registre a origem e mantenha
   em `backlog`; sua criação não autoriza executá-las.
8. Conclua apenas com todos os critérios atendidos e evidências registradas.
   Flows exigem a execução completa definida em AGENTS.md; impedimento de ambiente
   mantém a validação pendente. Para alterações exclusivas do agente, use planning
   e QA, sem etapa de desenvolvimento ou execução de pipelines.
9. Atualize o índice na mesma entrega que muda título, classificação, prioridade,
   status ou próxima etapa. Em divergências, o arquivo da tarefa é a fonte de
   verdade: reconcilie o índice. Preserve histórico de tarefas encerradas.

Mantenha uma única tarefa em execução por vez para este agente. Ao retomar um ID,
leia seu arquivo, verifique o estado real do Git e as evidências anteriores antes
de continuar. Registrar uma tarefa não autoriza push, publicação ou ações externas.
