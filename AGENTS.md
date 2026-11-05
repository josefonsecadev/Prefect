# Agent

Agente único do projeto; responda em português do Brasil, com clareza e foco no
resultado. Priorize desempenho, disponibilidade e tecnologias open source.
Instruções explícitas do usuário prevalecem sobre os guias locais.

## Contexto e leitura sob demanda

- Fonte de trabalho do agente: `.agents`. Melhorias exclusivas do agente passam
  por planejamento e QA, sem desenvolvimento de produto nem execução de pipelines.
- Consulte somente as seções pertinentes: arquitetura em
  `.agents/knowledge/planning.md`, execução em `.agents/knowledge/dev_senior.md` e
  revisão/commit em `.agents/knowledge/qa_chato.md`. Não carregar os três por rotina.
- Reutilize conteúdo já lido no chat; releia apenas se mudou, foi compactado sem
  detalhe suficiente ou surgiu uma dúvida concreta. Use `rg` e trechos delimitados;
  amplie a leitura para compreender contratos/usos antes de editar com segurança.
- Consulte backlog `.agents/tasks/README.md` e somente as tasks relacionadas.
  Perguntas informativas e operações Git de entrega não exigem nova task.

## Fluxo econômico

1. Defina em poucas linhas objetivo, flows/camadas, recorte, arquivos e aceite.
   Planejamento inicial de até um minuto; detalhe sob demanda. Mudança de regra de
   negócio ou arquitetura fora do pedido exige esclarecer antes de implementar.
2. Faça a menor entrega que resolve o pedido. Não ampliar escopo para melhorias,
   novas camadas ou modos de persistência sem confirmar que são necessários.
3. Uma branch por demanda; reutilize checkout adequado. Etapas pequenas, até cinco
   arquivos e 5.000 tokens estimados, incluindo controle; estimativa não é meta de gasto.
   Revise cada etapa; commits por entrega coerente, sem branch/commit por microação.
4. Registre demanda antes de alterar e atualize task/índice em marcos, falhas relevantes
   e encerramento; não a cada comando. Fonte de verdade é a task. Preserve histórico.
5. Agrupe consultas independentes. Operação longa: grave logs em caminho local
   ignorado e retorne estado, run ID, causa e trecho relevante (normalmente 20–40 linhas).
   Evite dumps e stack traces repetidos; amplie somente se necessário ao diagnóstico.
6. Acompanhe processos com esperas de 20–30s, ajustáveis à duração, ou eventos de
   término. Evite polling a cada poucos segundos e múltiplos comandos pendentes
   consultando a mesma falha. Dê atualização breve ao usuário quando houver avanço
   ou impedimento, respeitando as exigências de comunicação do ambiente.
7. Retry externo é limitado. Esgotou tentativas e confirmou mesma falha sem evidência
   nova: registre bloqueio e avance no trabalho independente. Reexecute após correção
   concreta ou mudança da condição; não repetir chamadas idênticas indefinidamente.
8. Ao encerrar: resultado, validação, pendências, próximo passo e commit quando houver.
   Para outra demanda independente, prefira chat novo com resumo curto de retomada;
   não criar chats automaticamente nem transferir contexto integral.

## Skills

Leia somente as skills aplicáveis, uma vez enquanto o conteúdo continuar disponível.
Referências internas apenas para a operação atual. Skills atualizadas nesta revisão:

| Skill | Quando usar | Caminho |
|---|---|---|
| Arquitetura de Software | Contratos e mudanças transversais | `.agents/skills/arquiteto-software/SKILL.md` |
| Engenharia de Dados | Implementar, diagnosticar ou executar flows | `.agents/skills/engenheiro-dados/SKILL.md` |
| Gestão de Tasks | Registrar, dividir e retomar alterações | `.agents/skills/gestao-tasks/SKILL.md` |
| Graphify | Navegar código, arquitetura e relações | `.codex/skills/graphify/SKILL.md` |

QA utiliza o knowledge citado acima. Referências legadas a skills em `agents/skills/`
sem ponto não comprovam disponibilidade; se ausentes, use os guias disponíveis sem
inventar instruções. Registre aqui novas skills/knowledge; não duplicar seus conteúdos.

## Contratos do projeto

Arquitetura alvo: Prefect + DuckDB + RustFS (S3) + Iceberg/Polaris + Trino para Ouro;
instalação nova, sem migração de legado. PostgreSQL persiste somente o catálogo.
Um flow por vez. Meta de 2GB depende de medição real; limites não provam capacidade.
Modos e exceções aprovados estão no planning/task; a instrução atual do usuário
sobre manter serviços ligados prevalece sobre a janela automática histórica.
Preserve dados, credenciais, recortes e mudanças preexistentes; sem segredos no Git
ou logs. Push/publicação apenas com autorização. Não reescrever histórico.

## Validação dos flows

- Não criar testes, mocks, fixtures ou simulações sem pedido explícito.
- Concluir alterações planejadas e reproduzir o flow completo pelo orquestrador,
  ambiente e perfil debug; testes isolados/compilação não substituem o aceite.
- VS Code usa `.vscode/launch.json` e `.venv` do checkout. Sem adaptador disponível,
  execute o mesmo módulo com `.venv/Scripts/python.exe` e variáveis do perfil.
  Não executar launcher debugpy isolado nem usar caminhos/portas de outra instalação.
- Conferir serviços necessários ao modo escolhido e endpoints host/container.
  Timeout do terminal não significa fim do run: verificar processo/Prefect antes
  de repetir, evitando duas execuções do mesmo recorte.
- Falha real: relatar causa provável, corrigir o necessário e reproduzir até terminal
  sem falhas. Impedimento externo/decisão pendente mantém aceite bloqueado; não fabricar
  dados ou declarar flow aprovado pela saúde dos containers.

## Web e grafo

Para pesquisar/ler páginas, use busca/navegador nativos; não criar scripts de scraping.
Isso não proíbe executar pipelines de coleta já autorizados pelo usuário.
`/graphify` invoca a skill antes das demais ações. Com grafo existente, consultar
`query`, `path` ou `explain` antes da leitura ampla; wiki para navegação e
GRAPH_REPORT apenas quando necessário. Mudanças geradas por hooks são esperadas.
Após código, usar `graphify update .`; se CLI/grafo faltar, registrar uma vez o
impedimento e seguir por leitura direcionada, sem tentativas repetidas ou instalação
fora do escopo. O grafo fica em `graphify-out/`.
