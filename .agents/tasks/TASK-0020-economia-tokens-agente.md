# TASK-0020 — Reduzir contexto e trabalho repetido do agente

- Status: concluida
- Categoria: agentes
- Tipo: melhoria
- Etiquetas: [agentes, tokens, skills]
- Prioridade: P1
- Complexidade: SIMPLES
- Origem: usuário autorizou aplicar as medidas de economia após consumo excessivo na TASK-0019.
- Criada/atualizada em: 2026-11-04
- Dependências: nenhuma; revisão exclusiva de instruções, planning e QA.

## Objetivo e escopo
Reduzir leituras, saídas, polling e burocracia sem enfraquecer escopo, segredos,
preservação de dados, revisão ou aceite real dos flows. Não alterar modelo, plugins,
código dos pipelines nem prometer percentual de economia de tokens/cota.

## Etapas
- E01: 3.000 tokens estimados, até cinco arquivos: AGENTS.md, dev_senior.md,
  qa_chato.md, esta tarefa e índice. Instruções comuns concisas e uma branch por demanda.
- E02: 3.000 tokens estimados, até cinco arquivos: skills Gestão de Tasks,
  Arquitetura e Engenharia de Dados, planning.md e esta tarefa. Alinhar leitura
  direcionada, escopo, acompanhamento e retomada. Estimativas incluem avaliação.
- Mesma branch codex/agente-economia-tokens; commits por entrega coerente, sem push solicitado.

## Aceite
- [x] Instruções sem obrigatoriedade de releitura integral ou branch por etapa.
- [x] Logs completos locais, resumos limitados, polling espaçado e falhas externas limitadas.
- [x] Preservados execução completa dos flows, revisão de diff, segredos, idempotência e registro de evidências.
- [x] Skills alinhadas e catálogo AGENTS atualizado; sem novo knowledge/skill.
- [x] Revisão documental/diff e comparação de tamanho, sem confundir tamanho com tokens faturados.

## Retomada
E01 em andamento. Evidência prevista: diffs e tamanho dos documentos; nenhum pipeline necessário.

E01: regras comuns e guias dev/QA enxugados; branch única, leitura sob demanda e validação proporcional. Revisão documental sem pipelines; comparação inicial dos seis guias: 36.875 caracteres. E02 segue na mesma branch.

## E02 e avaliação final
- Skills Gestão de Tasks, Arquitetura e Engenharia de Dados alinhadas ao AGENTS:
  leitura direcionada e reutilizada, referências sob demanda, uma branch, resumos,
  polling espaçado, limite de falha externa e resumo curto para retomada.
- planning.md não precisou mudar: conserva contratos da arquitetura; regra de leitura
  está no AGENTS e skills. Escopo final E02: três skills, tarefa e índice (cinco).
- Comparação dos seis guias: 36.875 → 19177 caracteres; redução textual de
  48%. Não mede tokens faturados nem promete economia percentual da cota.
- QA documental aprovada: removidas exigências de releitura integral/branch por etapa;
  preservados segredos, dados, idempotência, escopo, validação real, revisão de diff e
  autorização de push. Skills atualizadas constam no AGENTS. Nenhuma skill/knowledge novo.
- Checagens: diff whitespace, frontmatter e coerência das instruções; sem pipelines,
  alterações de modelos/plugins ou testes de produto. Próximo passo: aplicar nas demandas.
