# Desenvolvimento Sênior

## Preparação
- Use contrato aprovado na task: resultado, escopo, recorte, arquivos, comportamentos
  a preservar e aceite. Consulte planning somente nas seções afetadas, sem releitura
  se o conteúdo atual já estiver no contexto.
- Verifique Git e leia trechos afetados/usos diretos; amplie até entender contratos
  e efeitos. Preserve alterações preexistentes. Etapa até cinco arquivos, incluindo
  controle. Uma branch por demanda conforme AGENTS.md.
- Decisão essencial ausente ou mudança de negócio/arquitetura: esclarecer antes da
  implementação dependente. Continue trabalho independente dentro do pedido.

## Execução
- Menor alteração necessária; sem refatorações, dependências ou funcionalidades
  paralelas. Funções específicas ficam no pipeline; abstrações compartilhadas só
  para capacidade realmente comum.
- Valide entradas/SQL, use tipos do Python do projeto, preserve schemas/recortes e
  idempotência. Falhas devem propagar com contexto, sem segredos ou sucesso aparente.
- Não introduzir retries para erros de contrato. Operações externas com timeout;
  retries transitórios limitados, sem reiniciar bateria idêntica ao esgotá-los.
- Leitura, logs e acompanhamento seguem orçamento de contexto do AGENTS.md. Salve
  saída completa em local ignorado; apresente trecho causal e run ID. Não reconstruir
  imagem nem repetir verificações sem alteração que justifique.

## Validação e entrega
- Para flows, seguir exclusivamente a validação real definida no AGENTS.md após
  concluir implementação. Não criar testes/fixtures/mocks sem pedido, nem usá-los
  para substituir o orquestrador. Demais mudanças: check proporcional ao risco.
- Corrigir erro causal e repetir flow completo; em bloqueio externo/decisão pendente,
  registrar condição de retomada, sem declarar aceite. Timeout não autoriza duplicar run.
- Atualize tarefa em marcos: comportamento, arquivos, comando/recorte/run ID, estado,
  evidências e próximo passo. Não colar logs integrais no controle.
- Revise diff completo da entrega, segredos e escopo; consulte QA pertinente uma vez.
  Informe limitações. Commits por entrega coerente após revisão; push só autorizado.
