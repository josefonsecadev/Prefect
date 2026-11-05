# TASK-0019 — Executar flows de dados com Parquet direto no RustFS

## Identificação
- Status: em_execucao
- Categoria: pipelines
- Tipo: melhoria
- Etiquetas: [prefect, rustfs, parquet, duckdb, camara-deputados]
- Prioridade: P1
- Complexidade: TEM QUE PENSAR
- Origem: usuário pediu subir serviços, executar flows e corrigir erros para versão utilizável, salvando Parquet no RustFS sem validar catálogo/Trino agora.
- Criada em: 2026-11-04
- Atualizada em: 2026-11-04
- Dependências: Docker, RustFS e Prefect Server saudáveis; .venv Python 3.14.6 existente.

## Contrato aprovado nesta demanda
- Implementar modo explícito PIPELINE_STORAGE_FORMAT=parquet; manter iceberg como default existente. Não consultar/autenticar catálogo neste modo nem exigir suas credenciais.
- Bronze preserva contratos existentes (legislaturas Parquet, deputados JSON paginado, despesas ZIP CSV). Prata dos três e Ouro de despesas em Parquet tipado no RustFS.
- Destino: s3://<camada>/<projeto>/<pipeline>/<tabela>/<coluna>=<recorte>/data.parquet; tabela sem recorte usa <tabela>/data.parquet. Namespace de arquivos independente das tabelas Iceberg. Identificadores/recortes validados.
- Um flow por vez. Reprocessamento substitui a mesma chave do recorte somente após gerar Parquet local completo e validar leitura/schema/contagem; não apagar antes de upload. Leituras internas dos flows usam os Parquets neste modo, sem catálogo.
- Legislaturas antes de deputados; validar legislatura de 2025, despesas de 2025 (ano fechado). Flow de manutenção Iceberg não executado, por ser exclusivo do catálogo fora do escopo.
- Validar leitura remota dos Parquets, contagens/schema, somas Prata/Ouro e reprocessamento do mesmo recorte sem duplicação. Nenhum teste artificial, mock ou script substitui orquestradores reais.
- Executar entrypoints locais pela .venv com variáveis do perfil de debug quando não houver adaptador VS Code. Corrigir menor causa real e repetir até Completed.
- Prefect Server fica ligado; Worker deve registrar deployments válidos e permanecer disponível para uso. Não executar carga de estresse nem validar Trino/catalogação/Iceberg.
- Limites: modo Parquet não fornece transações/snapshots multiobjeto Iceberg; escrita serial, um objeto por recorte. Não alegar aceite das TASK-0006/0009 em Iceberg.

## Critérios de aceite
- [ ] RustFS e Prefect prontos e Worker operacional sem erro de deployment 422.
- [ ] Legislaturas, deputados e despesas completos terminam Completed em modo Parquet.
- [ ] Parquets remotos legíveis, schemas/contagens coerentes e Ouro reconciliada.
- [ ] Reprocessamento mantém estado lógico por recorte, sem afetar outros recortes.
- [ ] Configuração e comandos documentados, catálogo/Trino explicitamente não validados.

## Etapas
- E01 — Planejamento: 2.000 tokens; esta tarefa, índice e planning.md (três arquivos). Avaliação documental e commit em branch própria.
- E02 — Persistência compartilhada: 4.500 tokens; utils/config.py, utils/conexoes.py, utils/pipeline.py, esta tarefa e índice (cinco). Implementar modo, escrita/readback e leitura de dependências sem catálogo; sem avaliação isolada de flow.
- E03 — Operação e consumidores: 4.500 tokens; até três arquivos de implementação/configuração (Ouro, prefect.yaml e perfil debug), esta tarefa e índice. Corrigir consumidores para evitar catálogo, deployment e endpoints; dividir se precisar exceder.
- E04 — Reprodução completa: 4.500 tokens por flow; esta tarefa, índice e até três correções diretamente causais. Desdobrar E04 por flow e repetir falhas reais até terminal sem falha; não criar testes.
- E05 — Documentação e QA: 3.000 tokens; README.md, .env.example, esta tarefa e índice (quatro). Registrar run IDs, artefatos, limites e pendências. Grafo em etapa própria após código conforme disponibilidade da ferramenta.
- Estimativas incluem leitura/execução/avaliação; cada etapa até cinco arquivos e branch/commit próprios. Código entregue entre etapas não equivale ao aceite do flow.

## Retomada
- Etapa atual: E01; serviços sendo iniciados sem dependências de catálogo.
- Próximo passo: E02 e E03, depois executar orquestradores completos e corrigir falhas.
- Nenhum flow executado ainda nesta demanda; engine responde.

## Histórico
| Data | Evento | Evidência |
|---|---|---|
| 2026-11-04 | Demanda registrada | Escopo explícito Parquet/RustFS sem catálogo/Trino |

## E01/E02 — Entrega de código (aceite de flow pendente)
- E01 aprovada: contrato explícito de Parquet independente, sem alterar default Iceberg.
- E02 implementada em config/conexoes/pipeline: modo validado, credenciais/extensão Iceberg dispensadas no modo Parquet, chave determinística por recorte, schema/count local e readback remoto, leitura de dependências e proibição de snapshot no modo direto.
- QA documental/diff sem testes isolados; avaliação executável será feita nos orquestradores completos após E03. Até cinco arquivos nesta etapa; índice mantém status em execução.
- Próxima etapa E03: Ouro deve usar _table_source, corrigir parâmetros deployment e perfil debug; depois execução real.

## E03 — Consumidores e operação
- Ouro usa fonte conforme modo, sem chamar catálogo em Parquet; deployment de manutenção omite valores null para parâmetros obrigatórios (entrada exigida no disparo).
- Perfis debug dos três flows com modo Parquet e endpoints host explícitos. Iceberg default preservado fora desses perfis.
- QA de diff aprovada para iniciar reprodução real; nenhum teste isolado criado. Próximo: E04/legislaturas.

## E04/Legislaturas — impedimento na fonte
- Run c9fefa50-af84-4cf1-b6e3-9c628be0c563 falhou por HTTP 504 no GET de legislaturas. Cache Prefect também tentava serializar DuckDB/self (não foi a causa terminal).
- Corrigido NO_CACHE nas tasks de Legislaturas, retries HTTP limitados a transitórios e Accept JSON explícito. Runs 29e4adb1-d131-455b-b206-9274fef24db6 e 02c3ac55-5415-4f63-b846-a8668448b9d4 esgotaram retries com 504. Não repetir indefinidamente nem substituir por dados falsos.
- Código revisado; validação executável de Legislaturas pendente da disponibilidade da API. Deputados depende da Prata de Legislaturas; não alegar aceite sem dados.
- Worker reconstruído com correção do deployment, quatro deployments registrados e ProcessWorker bb81604f-7d4a-4c1c-bd76-8ec4bf48854d conectado ao pool local. RustFS/Server saudáveis; somente estes e Worker ligados.
- Próximo: executar Despesas 2025, independente de Legislaturas, corrigindo erros concretos. Sem catálogo/Trino.

## E04/Despesas — primeira execução real
- Orquestrador 8592d37f-6675-43de-8594-fd7d80eed443: Bronze Completed; Prata Completed com readback Parquet (209081 linhas) em prata/camara_deputados/despesas/despesas/numAno=2025/data.parquet. Ouro falhou em validação preexistente: 937 linhas sem ideCadastro.
- Diagnóstico sobre Parquet real: 937 sem deputado, zero mês inválido, zero valor ausente. Nomes são lideranças partidárias; não descartar nem atribuir ID fictício. Usuário consultado sobre manter Ouro somente deputados com exclusões explicitamente reconciliadas ou ampliar contrato; decisão pendente.
- Correções independentes: NO_CACHE nas tasks de Despesas; falhar em HTTP não sucesso e ZIP inválido antes da escrita; logs Prata mostram formato correto. Não alterada regra Ouro até decisão.
- Reprodução completa pós-correção permanece pendente de tratamento explícito das lideranças; não afirmar versão utilizável integral.

## E04/Deputados — dependência ausente
- Run 3140b1bd-ff5a-4054-94c2-5512ec02715e falhou ao ler a Prata Parquet de Legislaturas, ausente devido aos 504 da fonte. Nenhum dado inventado nem fallback silencioso aplicado.
- E04 completa permanece pendente. Nenhum ajuste ao flow de Deputados foi feito nesta subetapa, pois ele não chegou à coleta.
