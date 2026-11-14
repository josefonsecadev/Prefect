# TASK-0015 — Criar executor e métricas para testes de carga

## Identificação
- Status: backlog
- Categoria: observabilidade
- Tipo: criacao
- Etiquetas: [stress, docker, memoria, cpu, latencia, capacidade]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário solicitou tasks para testes individuais e conjuntos, em carga baixa, média, alta e altíssima, para compreender comportamento em produção.
- Criada em: 2026-11-04
- Atualizada em: 2026-11-04
- Dependências: TASK-0012 para estabilização e fotografia dos recursos; detalhes de execução a fechar em E01.

## Objetivo e contexto
Implementar uma ferramenta Python de carga real e coleta correlacionada de métricas. Geradores fazem operações reais, sem mocks. Esta solicitação autoriza planejar testes; nenhuma carga é executada neste registro. Não substituir os aceites funcionais das TASK-0006/0009/0010.

## Escopo e contratos
- Referências: docker-compose.yml, infra/batch.py, TASK-0011/0012. O coletor atual do batch mede somente stats a cada cinco segundos; não cobre todo este contrato.
- Componentes propostos: stress/runner.py, stress/metrics.py e manifestos em stress/scenarios/. Evitar novos servidores de observabilidade e dependências sem necessidade demonstrada.
- Identificar cada rodada por run_id e seed; usar buckets/prefixos, namespaces, tabelas e pool de ensaio exclusivos. Nunca usar tabelas de negócio nem alterar permissões do consumidor Ouro para viabilizar carga.
- Saída bruta ignorada pelo Git em .prefect/runtime/stress/<run_id>/: manifest.json, operations.jsonl, metrics.jsonl e resumo. Versionar somente cenários e relatório sanitizado. Credenciais vêm do ambiente, sem headers/tokens/corpos sensíveis nos artefatos.
- Manifesto registra commit, imagens/digests, host/VM, CPU/RAM/swap, limites efetivos, volumes, espaço livre, versões, seed, tamanhos, concorrência, taxa alvo e efetiva, deadlines, retries, duração e estado de cache.
- Operação registra UTC e duração monotônica, serviço, cenário, degrau, fase, tentativa, bytes/linhas, status, erro categorizado e query_id/flow_run_id quando disponíveis. Contabilizar separadamente tentativas, retries, sucessos e operações lógicas.
- Modelo de carga explícito: taxa de chegada configurável com limite de concorrência e fila limitada; registrar atraso de agendamento, fila, rejeição e operações não enviadas. Diferenciar latência de serviço de latência fim a fim; não esconder saturação reduzindo silenciosamente a taxa oferecida.

## Métricas obrigatórias
- Por serviço/container: memória atual e pico, working set/cache discriminados, limite, memory.events (max/OOM/OOM kill), swap, CPU em cores equivalentes e percentual com denominador, throttling, processos/threads, rede e I/O em deltas.
- Host/WSL: RAM disponível/residente, CPU, PSI quando disponível, swap, espaço livre, disco/I/O e consumo do gerador/coletor. Somar memória com definição consistente, sem duplicar cache compartilhado; registrar lacunas de coleta.
- Por operação: vazão (ops/s, MB/s, linhas/s), latências p50/p95/p99/máxima, tamanho da amostra, fila, timeouts, cancelamentos, falhas e integridade. Não afirmar p99 confiável com amostra insuficiente; conservar eventos brutos.
- Eventos: healthchecks, indisponibilidade, restart, OOM, erros do catálogo/SQL/S3, tempo para recuperar prontidão e nível de recursos após retirada da carga.
- Amostragem inicial configurável de 1s; medir overhead do coletor e declarar que amostragem pode perder picos. Preferir high-water marks/counters nativos quando disponíveis, com ressalvas de reset/escopo.

## Quatro níveis de carga
- Baixo: estabelecer operação estável e referência funcional com um cliente e dados pequenos.
- Médio: ampliar concorrência, taxa e/ou dados de forma controlada, com margem observada.
- Alto: aproximar o ponto de saturação observado, mantendo limites declarados.
- Altíssimo: sobrecarga limitada para observar fila, rejeição, falhas e recuperação. Não significa desligar proteções ou executar carga ilimitada.
- E01 deve fixar valores numéricos de cada cenário antes de execução. Rótulos descrevem carga oferecida, não percentuais presumidos de RAM/CPU. Variar uma dimensão por vez nos ensaios individuais; na carga conjunta usar mistura explícita.
- Protocolo inicial a calibrar: repouso 5min, aquecimento 1min, cada degrau 2min, recuperação até prontidão ou deadline; ao menos três repetições, com ordem e cache registrados. Ajustar durações/número de amostras na calibração e justificar alterações.

## Limites e riscos
- Antes de executar, fixar teto de duração, bytes/objetos/linhas, concorrência, filas, disco mínimo livre e deadlines. Modo padrão controlado; abortar novos envios ao atingir teto, mantendo coleta e finalização de operações até deadline.
- Ponto de ruptura e falhas/reinícios deliberados requerem janela e tolerância à indisponibilidade definidas; a escolha ainda está pendente. Não presumir autorização para derrubar a stack por este registro.
- Interrupção deve cancelar consultas pelo mecanismo suportado e verificar estados terminais de flows; não matar flow ativo por relógio. Cleanup só dos recursos listados no manifesto, idempotente e explícito, depois de preservar evidências.
- Se gerador/coletor saturar, classificar rodada limitada pelo cliente, sem atribuir capacidade ao servidor. Manter configuração fixa por rodada; mudanças de recursos geram outra rodada.

## Critérios de aceite
- [ ] Contrato de cenário/artefatos, quatro níveis numéricos e limites revisados antes da carga.
- [ ] Executor registra taxa oferecida/realizada, filas, falhas, cancelamentos e seed sem segredos.
- [ ] Métricas correlacionadas e overhead medido; indisponibilidade do daemon não bloqueia indefinidamente a coleta do host.
- [ ] Rodada curta real valida coleta, interrupção e identificação de dados sem tocar negócio.

## Etapas
Todas incluem leitura, execução, avaliação e controle; estimativas não garantem consumo.
- E01 — Contratos e limites: backlog; 3.500 tokens; até cinco arquivos (esta tarefa, índice e até três manifestos/documentos de cenário). Fechar valores, tolerância à falha, isolamento e esquema dos artefatos. Entrega: cenário revisável, sem carga.
- E02 — Executor: backlog; 4.500 tokens; até cinco arquivos (esta tarefa, índice, runner.py e até dois arquivos auxiliares). Entrega: agendamento limitado, registros, deadlines e cancelamento.
- E03 — Coletor: backlog; 4.500 tokens; até cinco arquivos (esta tarefa, índice, metrics.py e até dois auxiliares). Entrega: métricas container/VM/host e lacunas explícitas.
- E04 — Calibração: backlog; 3.500 tokens; até cinco arquivos (esta tarefa, índice e até três cenários/relatórios). Validar rodada real pequena e overhead, sem executar bateria completa. Saídas volumosas ficam ignoradas.

## Retomada
- Próxima ação: E01; confirmar limites e acesso às métricas no host/WSL. Nenhum código implementado.
- Validação pendente: todas; registro não significa capacidade comprovada.

## Histórico
| Data | Evento | Evidência |
|---|---|---|
| 2026-11-04 | Planejamento registrado | Solicitação explícita de testes de estresse |

## Avaliação do registro
- QA aprovada para planejamento/backlog: quatro tasks e índice (cinco arquivos), dependências sem ciclo, níveis e métricas explicitados, sem código, execução de carga ou segredos.
- Lacunas numéricas e tolerância a ruptura ficam em E01; por isso registros permanecem backlog. Sem alteração da arquitetura geral, criação de knowledge ou skill.
- Avaliação documental; nenhum teste de carga foi executado. Branch: codex/tasks-testes-carga. Commit local, sem push nesta demanda.
