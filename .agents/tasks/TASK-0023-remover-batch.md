# TASK-0023 — Remover execução por janela

- Status: concluida
- Categoria: orquestracao
- Tipo: melhoria
- Prioridade: P2
- Origem: usuário, 2026-11-05; Prefect deve permanecer ativo.

## Escopo e aceite
Remover infra/batch.py e infra/daily_flows.py e atualizar README e índice.
Manter deployments, flows, Compose e serviços atuais. Trabalhar somente na main,
conforme instrução explícita do usuário. Etapa de cinco arquivos incluindo controles.
Aceite: scripts removidos, instruções sem chamadas obsoletas e Compose válido.

## Contexto
TASK-0010 descreve a operação histórica por janela, agora abandonada; sua medição
de capacidade continua pendente. Nenhuma capacidade é comprovada nesta entrega.
Graphify CLI indisponível, já registrado nesta sessão; leitura direcionada utilizada.

## Resultado e QA
- Scripts removidos e README alinhado à operação contínua, mantendo profile processing.
- Compose validado com docker compose --profile processing config --quiet.
- git diff --check aprovado; sem chamadas aos scripts em README, Compose, prefect.yaml,
  infra ou .vscode. Referências históricas das tasks preservadas.
- Sem mudanças nos flows, serviços, agendamentos ou dados; nenhum pipeline executado.
- Etapa documental de encerramento: anotar decisão na TASK-0010, preservando histórico.
- Próximo passo: nenhum para a remoção; medição real continua pendente na TASK-0010.
