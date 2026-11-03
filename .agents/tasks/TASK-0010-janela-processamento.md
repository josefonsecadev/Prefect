# TASK-0010 — Automatizar janela Prefect e medir memória

- Status: backlog
- Categoria: orquestracao
- Tipo: criacao
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Origem: usuário mantém Trino ligado, permite desligar Prefect e autorizou executar pendências.
- Dependências: TASK-0005 para implementação, TASK-0008/0009 para aceite completo.

## Contrato

Agenda externa ao Prefect (Windows Task Scheduler ou systemd/cron) chama batch
com trava contra duplicação. Iniciar Server, aguardar API, iniciar Worker,
disparar flows sequenciais, acompanhar run IDs até estado terminal e parar somente
os serviços processing. Não desligar Trino, RustFS, Polaris ou PostgreSQL.
Em falha registrar causa e código de saída; nunca interromper run ativo por relógio.
Não cadastrar agenda real sem horário definido pelo usuário; entregar comando pronto.

## Etapas

- E01 (4.000 tokens): script de execução e profiles/concorrência; até três arquivos
  de implementação mais esta tarefa/índice (cinco). Entrega revisável, sem testes artificiais.
- E02 (3.500 tokens): rodar batch real e consultas com Trino continuamente ativo,
  medir RSS/cgroups/host e OOM. Registrar pico e memória disponível; até cinco arquivos.
- E03 (2.000 tokens): documentar agendamento no host, recuperação e limites;
  README, esta tarefa e índice (três).

## Aceite

- [ ] Batch real termina os flows em sequência, desliga Prefect depois e mantém Trino consultável.
- [ ] Segunda execução simultânea é recusada sem afetar a primeira.
- [ ] Falhas retornam código não zero e preservam diagnóstico sem segredos.
- [ ] Pico total de memória medido com carga real; meta 2GB avaliada explicitamente.
- [ ] Se exceder 2GB ou ocorrer OOM, registrar bloqueio de capacidade e não declarar aceite.

Próxima ação: implementar E01 depois da base. Nenhum horário de agenda foi presumido.

E01 implementada: `python -m infra.batch --year ANO` com trava exclusiva, profile
processing, espera de prontidão, flows síncronos sequenciais e desligamento somente
após checagem de runs ativos. Recusa assumir Prefect previamente ligado. Trino/base
não são parados. Coleta amostras de memória no diretório ignorado `.prefect/runtime`.
Ainda falta E02 real; Docker indisponível, portanto task não concluída.

QA: batch usa `compose run --rm prefect-worker` como executor de uso único;
não mantém poller adicional junto do processo do flow. O serviço worker tradicional
continua disponível para deployments manuais. Checagem final usa Server, que só
para se não houver runs ativos. Essa opção reduz duplicação de processos Python.
