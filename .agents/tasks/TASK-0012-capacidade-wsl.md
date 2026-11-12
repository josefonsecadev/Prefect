# TASK-0012 — Ajustar capacidade do WSL e orçamento da stack

## Identificação
- Status: em_revisao
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
- Status: em_revisao
- Estimativa: 2.500 tokens; até três arquivos (tarefa, índice e documento existente).
- Ações: comparar orçamento atual e meta, apresentar ganhos/custos e aprovar configuração antes de aplicar.
- Evidência: RAM VM/cgroups/host e contadores OOM/swap.
### E02 — Aplicar configuração aprovada
- Status: em_revisao
- Estimativa: 3.500 tokens; até cinco arquivos incluindo controles e configuração local.
- Ações: aplicar, reiniciar WSL em janela combinada, verificar prontidão e encaminhar carga à TASK-0010.
- Evidência: métricas antes/depois e nenhuma regressão de saúde.

## Retomada
- Próxima ação: usar medições finais da TASK-0011 e propor orçamento.
- Usuário autorizou explicitamente teste com 2GiB em 2026-11-04; aplicar e validar interfaces.

## Histórico
| Data | Evento | Evidência |
|---|---|---|
| 2026-11-04 | Registrada otimização | VM limitada a 1GiB |

## Execução autorizada — teste 2GiB
- Antes: MemAvailable=372932KiB, swap usada=30128KiB, PSI memory full avg10=24,61%. Pressão medida, causalidade das falhas ainda não comprovada.
- Configuração local alterada de 1GiB para memory=2GB, preservando quatro CPUs e backup local. Sem alterar limites dos containers.
- Restart e validação de interfaces em andamento; preservar volumes. Prefect deve permanecer ativo por solicitação do usuário.


### Resultado parcial do teste (2026-11-04)
- WSL reiniciado e MemTotal=1.949.300KiB confirmado; Docker Engine voltou a responder. Configuração anterior preservada em backup local.
- Prefect sob limite 160MiB: memory.events max=3173, oom=0, oom_kill=0; memory.swap.current=120631296 bytes. UI recusava conexão. Evidência de pressão por limite local, sem OOM.
- Correção local necessária para diagnóstico: PREFECT_SERVER_MEMORY=384m no .env ignorado, com backup em runtime. Recriado somente Server, sem apagar volume. Após startup: healthy, memory.events max=0, swap=2600960 bytes; uso aproximadamente 247,5MiB (amostra).
- Base voltou healthy: RustFS, PostgreSQL, Polaris e Trino. Bootstraps terminaram em 0.
- Validação HTTP interna: Trino /ui/ =200; RustFS /rustfs/console/config/ =200. RustFS raiz / retornava 403, portanto usar rota do console. Navegador automatizado indisponível por timeout; renderização/login no navegador não declarados validados.
- A pressão global WSL continuou durante startup mesmo em 2GiB (PSI full avg10 chegou a 61,97%, depois 13,22%); isso não prova estabilidade nem satisfaz meta com carga real.
- Amostra sem Worker: Server 247,5MiB; Trino 390,5MiB; Polaris 157,5MiB; PostgreSQL 23,29MiB; RustFS 80,99MiB. Não são picos sincronizados com flows.
- Worker está sendo iniciado; aguardar registro/polling antes de concluir diagnóstico. E02 permanece em execução; TASK-0010/E02 pendente. Nenhum teste artificial ou flow foi criado/executado.

### Encerramento da recuperação das interfaces
- Pelo Windows, respostas HTTP=200 confirmadas para http://localhost:4200/, http://localhost:9001/rustfs/console/config/ e https://localhost:8080/ui/. Trino verificado com certificado local ignorado apenas no comando de diagnóstico; navegação do usuário ainda pode mostrar aviso do certificado.
- Server permanece ligado e healthy. Base healthy; nenhum dado apagado. Login/renderização completa não validados pelo navegador, cuja ferramenta expirou.
- Worker iniciou, criou pool local e depois encerrou sem OOM: prefect deploy --all retorna 422 no deployment manutencao_iceberg_particionamento, com parametros camada/projeto/tabela=null incompatíveis com schema string. Não é falha de senha do front nem evidência de falta de RAM. Necessário corrigir registro de deployment antes de declarar Worker operacional.
- Resultado: interfaces recuperadas; E02 parcialmente validada, sem aceite de capacidade com flows. Estado da task em_revisao; próximo passo analisar parâmetros do deployment em prefect.yaml e executar validação real da TASK-0010 após correção autorizada no escopo próprio.
- QA: mudanças versionadas restritas a esta tarefa e índice. Configuração local .wslconfig e .env com backup, sem segredos no controle. Não alterar defaults do Compose sem validar capacidade. Commit local, sem push.
