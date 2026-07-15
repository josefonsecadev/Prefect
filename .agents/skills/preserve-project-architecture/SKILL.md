---
name: preserve-project-architecture
description: Preserva e evolui a arquitetura deste projeto de pipelines Prefect, DuckDB, MinIO, Iceberg e Lakekeeper. Use ao analisar, planejar, implementar ou revisar mudanças em pipelines Python, contratos de dados, flows e tasks Prefect, utilitários compartilhados, deployments, Docker Compose, armazenamento, catálogo, segurança, confiabilidade ou disponibilidade.
---

# Preservar a arquitetura do projeto

## Procedimento obrigatório

1. Ler [references/current-architecture.md](references/current-architecture.md) por inteiro antes de analisar ou alterar código, dados, configuração ou infraestrutura.
2. Conferir o pedido contra os arquivos atuais e executar `git status --short`; não usar a referência como substituta da inspeção do repositório.
3. Classificar o impacto em domínio de pipeline, componente compartilhado, contrato de dados, orquestração, deployment ou infraestrutura.
4. Identificar os invariantes afetados, o raio de impacto, a compatibilidade com deployments existentes e os riscos para confidencialidade, integridade, disponibilidade e recuperação.
5. Preferir a menor evolução incremental que reutilize os componentes atuais. Justificar qualquer nova abstração, dependência, serviço ou mudança de layout.
6. Definir validações proporcionais ao risco antes da implementação. Incluir rollback ou recuperação quando houver alteração de dados, schema, armazenamento ou infraestrutura.
7. Registrar divergências encontradas entre código e documentação; considerar código e configuração executável como fontes primárias do estado atual.

## Invariantes arquiteturais

- Preservar o fluxo fonte → Bronze no MinIO → transformação DuckDB → Prata no Iceberg/Lakekeeper.
- Reservar a camada Ouro para contratos destinados a clientes; não expor Bronze ou Prata diretamente como produto externo.
- Nunca criar, mover ou excluir diretamente objetos do warehouse Iceberg no bucket `iceberg`; publicar por meio do catálogo.
- Manter schemas e nomes do domínio em `info.py`, etapas em `bronze.py`, `prata.py` e, quando existir, `ouro.py`, além do encadeamento em `orquestrador.py`.
- Reutilizar `utils/config.py`, `utils/conexoes.py`, `utils/pipeline.py` e `utils/camara.py` quando a responsabilidade já existir.
- Preservar substituições idempotentes por partição e commits transacionais Iceberg. Tratar concorrência sobre a mesma partição antes de aumentar paralelismo.
- Tratar rede, armazenamento e catálogo como dependências falíveis. Exigir timeout, erro explícito, retries seguros e observabilidade quando aplicável.
- Não registrar, imprimir, versionar ou incluir valores de `.env`, credenciais ou tokens em planos e resultados.
- Tratar o Compose atual como ambiente local single-node, não como evidência de alta disponibilidade de produção.
- Preservar alterações preexistentes do usuário e evitar mudanças fora do escopo aprovado.

## Aplicação pelos papéis

- **Engenheiro de produção:** usar a referência para avaliar valor, risco, disponibilidade, segurança, freshness, qualidade e critérios de aceite; produzir plano macro sem editar arquivos.
- **Engenheiro de software:** confrontar o handoff de negócio com a arquitetura real; decidir viabilidade técnica e produzir plano detalhado, arquivos afetados, validações e rollback sem editar arquivos.
- **Desenvolvedor:** implementar somente um plano tecnicamente aprovado; preservar os invariantes, validar a mudança e reportar qualquer desvio antes de ampliar o escopo.

Seguir a sequência e os contratos definidos no `AGENTS.md` da raiz. Não executar as três etapas em paralelo, pois cada handoff é entrada obrigatória da etapa seguinte.

## Entrega mínima

Ao analisar ou planejar, informar:

- comportamento atual confirmado;
- mudança proposta e componentes afetados;
- aderência aos invariantes;
- riscos de dados, segurança e disponibilidade;
- critérios de aceite, validações e estratégia de recuperação;
- suposições e bloqueios ainda não resolvidos.

Ao implementar, acrescentar arquivos alterados, comandos executados, resultados das validações e desvios em relação ao plano aprovado.
