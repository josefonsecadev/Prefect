---
name: arquiteto-software
description: Planejar mudanças transversais, definindo responsabilidades, contratos, riscos e critérios de aceite antes do desenvolvimento.
---

# Arquitetura de Software

## Contexto e escopo
- Use AGENTS.md e somente seções pertinentes de `.agents/knowledge/planning.md`;
  não reler conteúdo atual já disponível no chat. Inspecione contratos e implementação
  afetados, com `rg` e trechos direcionados; amplie se houver lacuna real.
- Defina resultado, consumidor, volume/recorte/frequência, camadas, arquivos e aceite
  em poucas linhas. Planejamento inicial até um minuto, detalhando durante descoberta.
- Preserve o pedido: executar um flow não autoriza criar outra camada, modo de
  persistência ou regra de negócio. Antes de mudança essencial, apresentar opções
  com custo/benefício e aguardar escolha; continuar trabalho independente autorizado.

## Contratos necessários
- Fonte/acesso, entrada/saída, schema, particionamento, idempotência, concorrência,
  timeout/retry, falhas/recuperação, métricas, segurança e impacto operacional conforme
  pertinência. Não preencher seções irrelevantes ou inventar requisitos de produção.
- Usar tecnologias existentes; dependência nova exige necessidade demonstrada.
  PostgreSQL é backend interno Polaris, sem dados/regras de negócio dos pipelines.
- Consulte documentação oficial apenas para dúvida técnica concreta: Prefect,
  DuckDB, RustFS e Polaris. Não pesquisar capacidades estáveis já confirmadas na
  implementação nem carregar vários manuais por rotina.
- Falhas parciais e reprocessamento devem ter comportamento definido. Não mascarar
  erro como sucesso; respeitar responsabilidades Bronze/Prata/Ouro e credenciais.
- Registrar decisão relevante no planning antes do código, sem duplicar a task.
  Nova decisão de persistência/modelagem exige planejamento adequado; buscar skill
  especializada apenas se disponível e necessária, sem inventar arquivo ausente.

## Entrega
- Plano executável na task: objetivo/escopo, contratos/decisões, etapas pequenas,
  riscos e aceite observável. Até cinco arquivos e 5.000 tokens estimados por etapa;
  uma branch por demanda, sem forçar vários documentos/commits por pequena entrega.
- Para flows, executar orquestrador completo após implementação; não criar testes,
  mocks ou fixtures sem pedido explícito. Aceite funcional não é simulação.
- Não implementar enquanto houver decisão essencial pendente. Alteração só de agente
  passa por planning/QA, sem desenvolvimento de produto ou execução de pipelines.
