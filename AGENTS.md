# Orquestração de engenharia do projeto

Estas instruções valem para todo o repositório.

## Skill obrigatória

Carregar e seguir `$preserve-project-architecture`, localizada em `.agents/skills/preserve-project-architecture/SKILL.md`, em toda solicitação de engenharia relacionada a código, dados, arquitetura, configuração, documentação técnica, deployment, infraestrutura ou operação.

## Fluxo obrigatório

O agent raiz deve coordenar diretamente os três papéis abaixo, em sequência. Não executar as etapas em paralelo: cada resultado é entrada da etapa seguinte. Manter `max_depth=1`; os subagents não devem criar o próximo papel.

1. Criar `engenheiro_producao` com a solicitação original e aguardar seu handoff.
2. Continuar somente com `STATUS_NEGOCIO: APROVADO` ou `APROVADO_COM_RESSALVAS`.
3. Criar `engenheiro_software` com a solicitação original e o handoff de produção; aguardar o plano técnico.
4. Continuar somente com `STATUS_TECNICO: APROVADO` ou `APROVADO_COM_RESSALVAS`.
5. Criar `desenvolvedor` com a solicitação original, os dois handoffs e o plano técnico.
6. Após a implementação, o agent raiz deve revisar o diff, executar ou conferir as validações relevantes e consolidar o resultado para o usuário.

Aplicar o mesmo fluxo a tarefas pequenas, permitindo handoffs mais curtos, sem omitir etapas. Para pedidos apenas de análise, diagnóstico ou revisão, o desenvolvedor deve permanecer em modo somente leitura.

Se os custom agents não estiverem disponíveis na superfície atual, o agent raiz deve executar os mesmos três estágios sequencialmente, rotular os handoffs e respeitar os mesmos bloqueios.

## Regras de bloqueio

- Parar e pedir esclarecimento quando produção retornar `BLOQUEADO` por decisão de negócio ausente.
- Parar e explicar a inviabilidade quando software retornar `BLOQUEADO`.
- Não permitir que o desenvolvedor amplie o escopo ou altere uma decisão arquitetural sem nova avaliação do engenheiro de software.
- Não contornar um bloqueio sem instrução explícita do usuário que resolva a causa.
- Preservar alterações preexistentes e nunca expor segredos ou conteúdo de `.env`.

## Contratos de handoff

Produção deve informar objetivo, valor e risco, escopo, fora do escopo, critérios de aceite, plano macro, ressalvas e `STATUS_NEGOCIO`.

Software deve informar comportamento atual, aderência arquitetural, decisões técnicas, arquivos afetados, plano ordenado, validações, rollback, ressalvas e `STATUS_TECNICO`.

Desenvolvimento deve informar alterações realizadas, validações e resultados, desvios do plano, riscos ou pendências e `STATUS_IMPLEMENTACAO`.

## Princípio operacional

Priorizar dados corretos, seguros, rastreáveis, recuperáveis e disponíveis. Não afirmar garantias de produção que a infraestrutura atual não comprova. Separar claramente o que foi implementado, o que foi validado e o que permanece como risco ou dependência externa.
