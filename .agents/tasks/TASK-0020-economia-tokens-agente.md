# TASK-0020 — Reduzir contexto e trabalho repetido do agente

- Status: em_execucao
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
- [ ] Instruções sem obrigatoriedade de releitura integral ou branch por etapa.
- [ ] Logs completos locais, resumos limitados, polling espaçado e falhas externas limitadas.
- [ ] Preservados execução completa dos flows, revisão de diff, segredos, idempotência e registro de evidências.
- [ ] Skills alinhadas e catálogo AGENTS atualizado; sem novo knowledge/skill.
- [ ] Revisão documental/diff e comparação de tamanho, sem confundir tamanho com tokens faturados.

## Retomada
E01 em andamento. Evidência prevista: diffs e tamanho dos documentos; nenhum pipeline necessário.

E01: regras comuns e guias dev/QA enxugados; branch única, leitura sob demanda e validação proporcional. Revisão documental sem pipelines; comparação inicial dos seis guias: 36.875 caracteres. E02 segue na mesma branch.
