# TASK-0012 — Ajustar capacidade do WSL e orçamento da stack

## Identificação
- Status: backlog
- Categoria: infraestrutura
- Tipo: melhoria
- Etiquetas: [docker, wsl, memoria]
- Prioridade: P1
- Complexidade: TEM QUE PENSAR
- Origem: diagnóstico solicitado pelo usuário em 2026-11-04 (TASK-0011).
- Criada em: 2026-11-04
- Atualizada em: 2026-11-04
- Dependências: TASK-0011; articular aceite com TASK-0010/E02.

## Objetivo e contexto
O host possui 15,29 GiB físicos. .wslconfig limita WSL a 1 GiB e quatro CPUs; Engine reporta 940.691.456 bytes (897,1 MiB). Base permanente tem limites somados de 1.168 MiB (Trino 576 + Polaris 320 + RustFS 192 + PostgreSQL 80), antes do overhead Linux/Docker. Limites não representam consumo nem reserva, mas a capacidade atual oferece pouca margem. P1 por bloquear validação confiável da stack. Na tentativa real, Docker retornou HTTP 500 e WSL timeout 0x8007274c; OOM não comprovado.

## Escopo e referências
- Incluído: propor orçamento host/VM/containers, heap JVM, swap e margem durante bootstrap, repouso e processamento.
- Fora: trocar arquitetura, declarar que 2GB bastam ou executar flows duplicando TASK-0010.
- Referências: docker-compose.yml, infra/batch.py, configuração local .wslconfig (não versionar informações pessoais).
- Decisão pendente: orçamento aprovado da VM versus meta de 2GB; reinício WSL interrompe todas as distribuições.

## Critérios de aceite
- [ ] Orçamento documentado com margem explícita para kernel, daemon, cache e processos nativos.
- [ ] Bootstrap/repouso saudáveis e sem OOM após configuração aprovada.
- [ ] Pico com carga e Trino ativo validado na TASK-0010/E02, sem duplicar seu aceite.

## Etapas
### E01 — Planejar capacidade
- Status: backlog
- Estimativa: 2.500 tokens; até três arquivos (tarefa, índice e documento existente).
- Ações: comparar orçamento atual e meta, apresentar ganhos/custos e aprovar configuração antes de aplicar.
- Evidência: RAM VM/cgroups/host e contadores OOM/swap.
### E02 — Aplicar configuração aprovada
- Status: backlog
- Estimativa: 3.500 tokens; até cinco arquivos incluindo controles e configuração local.
- Ações: aplicar, reiniciar WSL em janela combinada, verificar prontidão e encaminhar carga à TASK-0010.
- Evidência: métricas antes/depois e nenhuma regressão de saúde.

## Retomada
- Próxima ação: usar medições finais da TASK-0011 e propor orçamento.
- Implementação não autorizada por este registro.

## Histórico
| Data | Evento | Evidência |
|---|---|---|
| 2026-11-04 | Registrada otimização | VM limitada a 1GiB |

