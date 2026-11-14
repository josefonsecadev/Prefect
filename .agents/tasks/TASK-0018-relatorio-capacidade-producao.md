# TASK-0018 — Analisar curvas de capacidade e orientar produção

## Identificação
- Status: backlog
- Categoria: observabilidade
- Tipo: investigacao
- Etiquetas: [stress, capacidade, producao, memoria, cpu, latencia]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário quer observar indicadores nos quatro cenários para entender situações de produção.
- Criada em: 2026-11-04
- Atualizada em: 2026-11-04
- Dependências: TASK-0016 e TASK-0017 com resultados; TASK-0015 com contrato de coleta.

## Objetivo e contexto
Transformar resultados medidos em curvas por serviço e stack, capacidade sustentável sob critérios explícitos, gargalos, margens e propostas de otimização. Distinguir capacidade observada no laboratório de recomendação de produção. Não prometer disponibilidade ou dimensionamento de cluster com dados de um host.

## Escopo e referências
- Entradas: artefatos identificados por run_id, cenários, métricas, falhas e manifesto das TASK-0015 a 0017.
- Saída: relatório sanitizado e gráficos/tabelas exportáveis, com comandos para reproduzir e referências aos artefatos locais. Não versionar dumps, credenciais, objetos sintéticos ou histórico bruto volumoso.
- Gráficos por nível e tempo: RAM atual/pico/limite, CPU/throttling, swap/PSI, latências p50/p95/p99, vazão, taxa de erros, filas, I/O/rede, ocupação/temporários/snapshots e recuperação. Separar aquecimento, regime, sobrecarga e recuperação.
- Distinguir oferecido/realizado, sucesso/retry, cliente/servidor, cgroup/VM/host e métricas faltantes. Exibir amostras e dispersão entre repetições; p99 sem amostra adequada deve ser marcado inconclusivo.
- Comparar individual versus conjunto, cache frio/aquecido e efeitos de volume/cardinalidade/tamanho de objetos. Uma rodada limitada pelo gerador não mede teto do serviço.
- Capacidade sustentável exige janela e critérios de latência/erros/recuperação definidos. Se SLO de produção, volume, crescimento, simultaneidade e hardware alvo não forem informados, usar apenas limites exploratórios identificados e listar dados faltantes. Não inventar SLO nem equivalência de rótulos com produção.
- Recomendações devem citar evidência, hipótese causal, alteração proposta, custo/risco, margem e rodada de confirmação. Aumento de recurso não é prova de causa; falha sem OOM não deve ser chamada OOM.
- Integrar TASK-0012 (capacidade), TASK-0013 (imagem), TASK-0014 (retenção) e TASK-0010 (batch/pico). Criar novas tasks somente para achados concretos, sem executar otimizações neste relatório nem duplicar backlog.

## Critérios de aceite
- [ ] Matriz serviço × baixo/médio/alto/altíssimo e comparativo individual/conjunto com limitações explícitas.
- [ ] Curvas e artefatos reproduzíveis, amostras/variação e eventos correlacionados.
- [ ] Limites observados, ponto de degradação/ruptura ou teto não atingido identificados sem extrapolação indevida.
- [ ] Integridade e recuperação avaliadas; falhas esperadas separadas de defeitos da ferramenta.
- [ ] Recomendações de produção condicionadas a SLO/workload/hardware; pendências e tasks com evidências atualizadas.

## Etapas
- E01 — Agregar resultados: backlog; 4.000 tokens; esta tarefa, índice e até três arquivos de análise/relatório. Verificar integridade das amostras e produzir tabelas sem descartar falhas/timeouts silenciosamente.
- E02 — Visualizar e interpretar: backlog; 4.500 tokens; esta tarefa, índice e até três artefatos/documentos. Produzir curvas, comparar repetições e formular hipóteses, destacando pressão/saturação por recurso.
- E03 — Recomendações e backlog: backlog; 3.500 tokens; esta tarefa, índice e até três tasks/documentos. Atualizar tarefas existentes ou dividir novos achados em etapa posterior para manter até cinco arquivos. Não executar otimizações.
- Estimativas incluem leitura, avaliação, escrita e controle; dividir antes de exceder limite.

## Retomada
- Próxima ação: aguardar resultados; solicitar perfil/SLO/hardware de produção antes de dimensionamento definitivo.
- Validações pendentes: todas; nenhum resultado de carga existe por esta task.

## Histórico
| Data | Evento | Evidência |
|---|---|---|
| 2026-11-04 | Registrada análise de capacidade | Objetivo explícito de compreender cenários de produção |
