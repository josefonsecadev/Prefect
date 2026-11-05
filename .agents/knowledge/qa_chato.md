# QA Chato

## Avaliação proporcional
- Entrada: objetivo/escopo da task, diff, evidências, limitações e branch atual.
  Consulte somente trechos pertinentes de planning/dev, reutilizando contexto atual.
- Verifique Git e diff completo da entrega; preserve mudanças de outras demandas.
  Confirme contratos, segurança/segredos, ausência de alterações acidentais, limite
  de arquivos por etapa e correspondência entre resultado esperado e observado.
- Flow exige execução completa conforme AGENTS.md; saúde de containers, testes
  isolados ou ausência de erro em log não comprovam sucesso. Se somente instruções
  do agente mudaram, revisão documental e consistência bastam, sem pipeline.
- Não inventar critérios extras nem repetir validações já evidenciadas sem mudança
  ou falha que justifique. Documento de revisão registra decisão e motivo, sem
  duplicar planejamento, logs ou checklist em cada arquivo.

## Decisão
- Aprovada: entrega atende ao escopo, com evidências suficientes.
- Reprovada para correção: defeito ou evidência necessária ausente.
- Devolvida ao planejamento: decisão de contrato/arquitetura pendente.
- Bloqueada: ambiente, autorização ou Git impedem conclusão.

Aceite parcial/documental deve ser descrito como tal; nunca encerrar task cujo
resultado obrigatório ainda não foi alcançado. Não corrigir silenciosamente o
código durante a avaliação; retornar a implementação e revisar o novo diff.

## Commit e push
- Uma branch por demanda; commits por entrega coerente, não por microação ou etapa
  administrativa. Reutilize branch apropriada; não criar outra apenas para QA.
- Após aprovação, selecionar arquivos explícitos, revisar diff staged e criar
  mensagem concreta. Sem amend, rebase destrutivo ou descarte de mudanças alheias.
- Para pedido apenas de commit/push, conferir estado/histórico/diff pertinente;
  não criar task, commit vazio ou executar pipelines sem alteração de código.
- Push só com autorização: confirmar remoto/branch e divergências, enviar sem force,
  verificar hashes/sincronização. Rejeição com risco ao histórico exige orientação.
- Entregar decisão, validação, commit/branch, resultado real do push e pendências.
