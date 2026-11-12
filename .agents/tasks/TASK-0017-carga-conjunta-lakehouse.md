# TASK-0017 — Executar carga conjunta e recuperação do lakehouse

## Identificação
- Status: backlog
- Categoria: observabilidade
- Tipo: criacao
- Etiquetas: [stress, capacidade, prefect, trino, rustfs, polaris, postgres]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário quer compreender comportamento da stack sob cenários de produção, com consumo baixo, médio, alto e altíssimo.
- Criada em: 2026-11-04
- Atualizada em: 2026-11-04
- Dependências: TASK-0015 e adaptadores/baselines individuais da TASK-0016; Worker operacional e validação funcional da cadeia antes da sobrecarga.

## Objetivo e contexto
Executar flows gravando Bronze/Prata/Ouro enquanto Trino consulta e clientes S3 operam. Comparar com baselines individuais e revelar contenção de CPU, memória, catálogo, rede, disco e gerador. Não extrapolar uma máquina Windows/WSL para capacidade de produção sem qualificar hardware/topologia/dados.

## Escopo e contrato
- Reutilizar runner, adaptadores, isolamento, artefatos e métricas da TASK-0015/0016; não criar outro framework. Arquivos previstos: stress/scenarios/conjunto.json e configuração de execução dedicada quando necessária.
- Quatro níveis com mistura numérica de taxa S3, consultas Trino, cardinalidade/volume de flow e operações de catálogo; publicar percentuais da mistura por rodada. Não escalar todos os fatores sem registrar a composição.
- Concorrência de flows continua um por vez, com fila visível. Aumentar paralelismo de flows somente em pool experimental isolado e decisão explícita; não alterar pool local silenciosamente.
- Matriz inclui ingestão dominante, leitura dominante e mistura equilibrada, com snapshot estável versus commits durante consultas. Resultados SQL devem corresponder a um snapshot válido, sem exigir que consultas concorrentes vejam o mesmo snapshot.
- Executar baseline, aquecimento, quatro degraus, sustentação e recuperação; duração de sustentação fixada após calibração, suficiente para observar acumulação de memória, snapshots, temporários e filas. Repetições e cache conforme TASK-0015.
- Antes de cada rodada conferir ausência de processamento de negócio, saúde/credenciais, dados sintéticos e espaço. Não disparar agenda real nem sobrecarregar fonte externa.
- Configuração efetiva fixa por rodada; primeiro registrar WSL 2GiB e Server 384MiB locais se ainda vigentes, sem tratar como referência universal. Comparações de limites são rodadas distintas, articuladas à TASK-0012.
- No modo controlado, parar novos envios por limites explícitos e acompanhar operações ativas; no altíssimo, falhas de saturação são classificadas. Injeção de queda, restart manual ou ruptura deliberada é cenário adicional com janela/tolerância aprovadas, ainda pendentes, não pré-requisito para começar o modo controlado.
- Quantificar interferência: p95/vazão conjunta versus individual com dataset/cache equivalentes, fila e tempo de recuperação. Não atribuir erro ao serviço que apenas propagou falha de dependência.

## Critérios de aceite
- [ ] Cada mistura tem quatro níveis, taxa oferecida/efetiva, limites e repetições documentados.
- [ ] Métricas simultâneas de todos os containers e host/WSL, incluindo gerador, sem confundir soma de limites com capacidade.
- [ ] Pico, saturação, erros, filas, perda de prontidão, integridade e recuperação registrados mesmo quando coleta/API falhar.
- [ ] Execução funcional conjunta com flow completo termina sem falhas; cenários de sobrecarga reportam resultado real e razão de interrupção.
- [ ] Recuperação confirma consultas válidas, commits íntegros, ausência de runs órfãos e dados de negócio preservados.
- [ ] Resultados alimentam TASK-0018 e complementam medição da TASK-0010 sem declarar seu aceite automaticamente. Prefect permanece ligado neste ensaio, conforme pedido atual.

## Etapas
- E01 — Matriz de misturas: backlog; 3.500 tokens; esta tarefa, índice e até três cenários/documentos. Fixar valores, sustentação, recuperação e critérios de parada; registrar decisões pendentes.
- E02 — Coordenar cargas: backlog; 4.500 tokens; esta tarefa, índice e até três arquivos runner/cenários. Reutilizar adaptadores e validar controle de ciclo de vida/cancelamento.
- E03 — Rodadas: backlog; 4.500 tokens por mistura; esta tarefa, índice e até três cenários/relatórios. Desdobrar por mistura e repetição antes de execução se exceder orçamento. Coletar quatro níveis e recuperação, sem código paralelo de negócio.
- E04 — Consolidar comparação: backlog; 3.500 tokens; esta tarefa, índice e até três relatórios/configurações. Conferir evidências e passar artefatos à TASK-0018.
- Todas as estimativas incluem leitura, execução, avaliação e controle; resultados brutos ficam ignorados.

## Retomada
- Próxima ação: aguardar baselines individuais e fechar E01. Nenhuma carga executada por esta task.
- Riscos: indisponibilidade local, swap, disco/snapshots e gerador limitante; mitigação por tetos e isolamento da TASK-0015.

## Histórico
| Data | Evento | Evidência |
|---|---|---|
| 2026-11-04 | Registrada carga conjunta | Solicitação explícita do usuário |
