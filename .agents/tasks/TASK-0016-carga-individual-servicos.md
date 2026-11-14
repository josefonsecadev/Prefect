# TASK-0016 — Implementar e executar carga por serviço

## Identificação
- Status: backlog
- Categoria: observabilidade
- Tipo: criacao
- Etiquetas: [stress, rustfs, trino, prefect, duckdb, polaris, postgres]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário quer observar limites individuais em consumo baixo, médio, alto e altíssimo.
- Criada em: 2026-11-04
- Atualizada em: 2026-11-04
- Dependências: TASK-0015; prontidão/identidades de TASK-0005/0008. Cenário Prefect depende da correção do HTTP 422 no deployment de manutenção registrado na TASK-0012.

## Objetivo e contexto
Produzir curvas por serviço e identificar gargalos e recuperação com o protocolo/métricas da TASK-0015. Isolar a carga aplicada mantendo dependências necessárias; consulta Trino também usa catálogo/storage, e flow usa toda a cadeia. Não chamar dependências compartilhadas de isolamento físico.

## Escopo e cenários
- RustFS (stress/rustfs.py): PUT/GET/LIST e, se necessário, multipart; variar tamanhos, número de objetos e concorrência; medir latência/vazão por operação e verificar checksum/conteúdo. Distinguir CPU/RAM do payload no gerador da do servidor; leitura deve consumir resposta e liberar conexão. Não criar objetos infinitamente.
- Trino (stress/trino.py): dados Iceberg sintéticos pré-carregados; SELECT filtrado, scan/agregação e join com cardinalidades conhecidas. Separar fila, execução e transferência do resultado; capturar query_id, bytes/linhas lidos, memória e spill quando expostos. Consumir resultados em lotes, conexão por cliente e cancelamento por deadline. Separar dataset/cache frio e aquecido, sem limpar cache global indiscriminadamente.
- Prefect Server: submissões e consulta de estado em pool de ensaio, preservando um flow executor por vez no padrão. Medir latência da API, fila, transições, atraso até Running e estados terminais; retries não escondem falhas.
- Worker + DuckDB: flow sintético real Bronze → Prata → Ouro por orquestrador dedicado, seed e recorte explícitos. Variar linhas, largura, cardinalidade e custo de agregação; gerar fonte local sem sobrecarregar APIs públicas. Verificar contagens, soma/checksum, reprocessamento idempotente e snapshot. Medir Worker/DuckDB juntos e, quando possível, processo, buffers e temporários separadamente, sem duplicar memória do cgroup.
- Polaris: carga REST de metadados e commits Iceberg válidos sobre tabelas de ensaio. Distinguir OAuth da operação; medir cache, taxa/latência de commits, conflitos esperados, retries e crescimento de snapshots. Erros esperados de concorrência continuam registrados.
- PostgreSQL: avaliar separadamente recursos, conexões, locks/waits, transações, cache e I/O durante a carga Polaris. Microbenchmark SQL isolado somente em banco/volume descartável e schema de ensaio, sem escrever diretamente no schema interno Polaris. Planejar seu custo/isolamento em E01 antes da execução. Não adicionar banco de negócio.
- Incluir baseline dos demais serviços para medir efeito indireto. Não inferir capacidade por comparação de imagens ou limites configurados.
- Artefatos/limites/níveis definidos pela TASK-0015; referências adicionais: docker-compose.yml, prefect.yaml, pipelines/, utils/. Usar Engenharia de Dados para o orquestrador.

## Critérios de aceite
- [ ] Matriz com quatro níveis numéricos para cada serviço e dependências explicitadas.
- [ ] Cada cenário executado com métricas RAM/CPU/latência/pico/vazão/falhas/recuperação e dataset reproduzível.
- [ ] Baixo/médio funcionalmente íntegros; alto/altíssimo registram degradação ou limite alcançado, sem inventar ponto de ruptura quando o teto da rodada impedir alcançá-lo.
- [ ] Flow sintético completo reproduzido pelo ambiente/perfil debug do projeto até terminal sem falhas no cenário funcional. Falha induzida em estresse é evidência de limite, não substitui esse aceite.
- [ ] Recuperação, integridade, espaço temporário e dados remanescentes conferidos. Dados de negócio preservados.

## Etapas
Estimativas incluem leitura, implementação, reprodução e controle; dividir se ultrapassar cinco arquivos.
- E01 — Matriz individual: backlog; 3.500 tokens; esta tarefa, índice e até três manifestos/documentos. Fixar volumes, taxa, concorrência, SQL e deadlines para cada nível; decidir banco descartável do PostgreSQL e pré-requisitos de permissões.
- E02 — Adaptador S3: backlog; 4.000 tokens; esta tarefa, índice, stress/rustfs.py e até dois auxiliares/cenários. Validar operações e integridade reais.
- E03 — Adaptador SQL: backlog; 4.500 tokens; esta tarefa, índice, stress/trino.py e até dois auxiliares/cenários. Validar resultados, consumo completo e cancelamento.
- E04 — Flow sintético: backlog; 4.500 tokens; esta tarefa, índice e até três arquivos de pipeline. Se camadas precisarem de mais arquivos, decompor antes de implementar. Preservar concorrência padrão e executar flow completo depois das alterações.
- E05 — Catálogo: backlog; 4.000 tokens; esta tarefa, índice e até três adaptadores/cenários Polaris. Validar criação/commit e separar falha de contrato de saturação.
- E06 — Banco interno: backlog; 3.500 tokens; esta tarefa, índice e até três configurações/adaptadores de ensaio. Executar carga PostgreSQL no ambiente descartável aprovado e coleta durante Polaris, sem alterar schema interno.
- E07 — Bateria individual: backlog; 4.500 tokens por rodada/serviço; esta tarefa, índice e até três cenários/relatórios. Repetir E07 em subetapas por serviço antes de executar; respeitar teto, quatro níveis e repetições. Entrega: resultados brutos e síntese sanitizada para TASK-0018.

## Retomada
- Próxima ação: após TASK-0015, detalhar E01; correção Worker é pré-requisito do cenário Prefect, não bloqueia desenvolvimento independente S3/SQL.
- Nenhum teste implementado ou executado; falha 422 ainda pendente no último diagnóstico.

## Histórico
| Data | Evento | Evidência |
|---|---|---|
| 2026-11-04 | Registrada carga individual | Demanda explícita do usuário |
