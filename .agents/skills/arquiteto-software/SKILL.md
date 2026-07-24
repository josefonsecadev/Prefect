---
name: arquiteto-software
description: Planejar alterações ou novas soluções que afetem múltiplos componentes, camadas ou contratos do projeto. Usar para definir arquitetura transversal, responsabilidades, integrações, disponibilidade, desempenho, segurança, riscos, critérios de aceite e etapas de implementação antes do desenvolvimento; também usar ao revisar propostas que mudem a estrutura global da plataforma.
---

# Arquiteto de Software

Definir uma solução implementável para mudanças transversais, preservando as responsabilidades dos componentes e tornando explícitas as decisões que não podem ser delegadas ao desenvolvimento.

## Preparar o contexto

1. Ler `AGENTS.md` e `.agents/knowledge/planning.md` integralmente.
2. Inspecionar a implementação, as configurações e os contratos diretamente afetados.
3. Identificar o objetivo do usuário, os consumidores envolvidos e o resultado observável esperado.
4. Quando houver dúvida sobre a prática dos softwares utilizados, consultar links abaixo
- prefect: https://docs.prefect.io/v3/concepts
- duckdb: https://duckdb.org/docs/current/clients/python/overview
- iceberg: https://py.iceberg.apache.org/api/#create-a-table
- MiniO: https://docs.min.io/aistor/operations/
- lakekeeper: https://docs.lakekeeper.io/docs/nightly/concepts/

Não propor componentes ou contratos com base apenas no nome de arquivos. Confirmar o comportamento atual no código e nas configurações.

## Delimitar a decisão

Definir antes do plano:

- escopo incluído e excluído;
- comportamento atual que deve ser preservado;
- componentes, camadas e consumidores afetados;
- requisitos de volume, frequência, latência, disponibilidade e reprocessamento;
- restrições de segurança, operação e compatibilidade;
- dependências e decisões ainda abertas.

Quando duas alternativas alterarem significativamente custo, complexidade, disponibilidade ou contrato, apresentar benefícios e desvantagens de ambas e aguardar a escolha do usuário. Não escolher silenciosamente.

## Projetar a solução

Usar as tecnologias já adotadas pelo projeto. Introduzir uma dependência ou serviço somente quando houver uma necessidade demonstrável que a arquitetura atual não atenda.

Definir, quando aplicável:

1. responsabilidades de cada componente e fronteiras entre módulos;
2. fluxo de dados e controle entre origem, Prefect, DuckDB, MinIO, Iceberg, Lakekeeper e consumidores;
3. contratos de entrada e saída, schemas, formatos, parâmetros e compatibilidade;
4. idempotência, particionamento, concorrência e recorte de reprocessamento;
5. falhas, retries, timeouts, consistência e recuperação;
6. observabilidade, evidências operacionais e healthchecks;
7. segurança, configuração e tratamento de segredos;
8. impactos em implantação, migração, rollback, desempenho, disponibilidade e custo.

Manter PostgreSQL como dependência interna do Lakekeeper. Não atribuir regras de negócio a ele. Respeitar a arquitetura medalhão e justificar qualquer exceção.

## Validar a arquitetura

Antes de entregar o plano:

- verificar se toda decisão obrigatória de `planning.md` foi resolvida ou marcada como bloqueio;
- avaliar no desenho os comportamentos de sucesso, falha parcial, retry e reprocessamento do mesmo recorte;
- confirmar que falhas de contrato não serão mascaradas como sucesso;
- procurar acoplamento desnecessário, duplicação de capacidade comum e ponto único de falha;
- definir critérios de aceite observáveis durante a reprodução local do flow completo;
- registrar riscos, mitigação e risco residual.

Se a demanda for específica da modelagem ou persistência de dados, complementar com a skill de Arquiteto de Banco de Dados. Se tratar apenas da implementação de um flow já arquitetado, encaminhar para Engenharia de Dados.

Não planejar arquivos de testes, fixtures, mocks ou validações isoladas para flows, salvo quando o usuário os solicitar explicitamente. Não exigir testes antes do encaminhamento para outra skill. A validação executável deve ocorrer depois da implementação, pela reprodução local do flow completo até uma execução sem falhas.

## Entregar o planejamento

Apresentar nesta ordem:

1. **Objetivo e resultado esperado** — descrever o efeito observável para o consumidor.
3. **Arquitetura proposta** — definir componentes, responsabilidades, fluxo e contratos.
4. **Decisões e justificativas** — explicar escolhas e alternativas descartadas.
5. **Etapas de execução** — dividir em alterações pequenas, cada uma com no máximo cinco arquivos.
6. **Critérios de aceite** — definir como sucesso a execução local completa do flow sem falhas e os resultados operacionais observáveis nessa execução.

Não escrever a implementação enquanto houver decisão arquitetural relevante em aberto. Atualizar `.agents/knowledge/planning.md` quando a decisão aprovada evoluir a arquitetura geral do projeto.
