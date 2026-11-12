# TASK-0022 — Adotar .env fixo e remover gerador

- Status: concluida
- Categoria: infraestrutura
- Tipo: melhoria
- Prioridade: P2
- Origem: solicitação explícita do usuário em 2026-11-05.

## Escopo e aceite
Usar .env local fixo, preservando credenciais e ajustes existentes; remover
infra/init_env.py e atualizar instruções. Manter .env ignorado e .env.example
como referência. Até cinco arquivos, incluindo controles e configuração local.
Não alterar flows, volumes nem reiniciar serviços.

## Validação prevista
Conferir chaves sem imprimir valores; validar Compose com config --quiet;
revisar referências ativas e diff. Graphify CLI indisponível nesta sessão.

## Resultado e QA
- .env existente adotado como fixo, com comentário explicativo; valores preservados.
- Todas as chaves de .env.example presentes, sem valores vazios nem placeholders.
- Gerador removido e README atualizado para configuração manual de novas instalações.
- docker compose --profile processing config --quiet aprovado; git diff --check aprovado.
- .env confirmado ignorado pelo Git; nenhuma referência ativa ao gerador no README,
  Compose ou infra. Histórico desta task preserva o nome do arquivo removido.
- Sem alteração de flows, execução de pipelines ou reinício de serviços.
- Próximo passo: nenhum para esta demanda. Commit local, sem push.
