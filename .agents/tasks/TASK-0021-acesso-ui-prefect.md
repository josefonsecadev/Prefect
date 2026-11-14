# TASK-0021 — Corrigir conexão da interface Prefect

- Status: concluida
- Categoria: docker
- Tipo: correcao
- Prioridade: P1 — interface indisponível para o usuário
- Origem: usuário iniciou serviços e relatou “Unable to connect to Prefect server”.
- Data: 2026-11-04

## Objetivo e escopo
Corrigir somente o endereço da API entregue ao navegador pelo Prefect Server.
Arquivos: Compose, esta task e índice. Preservar volumes, serviços e flows.
Aceite: API saudável e ui-settings apontando para endereço acessível pelo host.

## Evidência inicial
- Container healthy; localhost:4200/api/health retorna HTTP 200.
- /ui-settings retorna api_url=http://prefect-server:4200/api, DNS interno Docker.
- Logs contêm erro SQLite database is locked; saúde atual responde normalmente.
- Graphify CLI indisponível; leitura direcionada do Compose utilizada.

## Resultado e QA
- PREFECT_UI_API_URL configurado no Server para http://localhost:${PREFECT_PORT:-4200}/api.
- Somente Server recriado com --no-deps; volumes e demais serviços preservados.
- API /api/health HTTP 200 true; /ui-settings HTTP 200 com api_url=http://localhost:4200/api; interface / HTTP 200.
- Diff revisado e git diff --check aprovado. Nenhum flow alterado ou executado.
- Renderização no navegador do usuário não verificada; recarregar a página para obter a configuração corrigida.
- Erro SQLite histórico não foi reproduzido na validação HTTP; fora desta correção de URL.
- Próximo passo: usuário recarregar http://localhost:4200. Sem push.
