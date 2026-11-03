# TASK-0009 — Publicar produto Ouro e validar consumo pelo Trino

## Identificação

- Status: backlog
- Categoria: dados
- Tipo: criacao
- Etiquetas: [ouro, prefect, duckdb, iceberg, polaris, rustfs, trino, bi]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: camada de acesso à Ouro solicitada, arquitetura Trino + Polaris aprovada.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: E01 pode iniciar após TASK-0003; implementação requer TASK-0006;
  validação de consumo requer também TASK-0008. Sem dependência circular entre tasks.

## Objetivo e contexto

Contrato inicial E01: despesas líquidas por deputado/mês, consumidor analítico SQL.
Chave (ano, mes, deputado_id=ideCadastro); nome representativo MIN(txNomeParlamentar)
para não dividir uma chave por variações de grafia. Quantidade de lançamentos é
COUNT(*), não contagem de documentos únicos. Valor = SUM(vlrLiquido) DECIMAL(18,2),
incluindo negativos e sem descontar vlrGlosa novamente. Não inventar deduplicação
de documentos sem chave confirmada. ID/ano/mês/valor inválidos falham, sem descarte.
Destino ouro_camara_deputados.despesas_mensais; partição ano e substituição apenas
do ano solicitado. Primeiro produto proposto na pergunta opcional e adotado como
padrão de implementação; usuário pode alterar antes da publicação de consumo.

Entregar uma tabela Ouro útil, gerada por flow real e consultável pelo consumidor
SQL no Trino. Não presumir Ouro existente nem apenas renomear/expor Prata. Projeto
nasce com dados novos: produto será calculado das fontes e camadas reconstruídas.
Preservar regras existentes e definir novas métricas explicitamente antes de codificar.
Referências: `pipelines/camara_deputados/`, `utils/pipeline.py`, `prefect.yaml`,
AGENTS.md e contratos TASK-0003. Usar Arquitetura e Engenharia de Dados.

## Etapas

Por etapa, até 5.000 tokens incluindo revisão/controle e cinco arquivos incluindo
esta tarefa e índice. Sem testes, fixtures, mocks ou scripts que substituam flows.

### E01 — Definir o primeiro produto Ouro

- Status: backlog; estimativa: 3.000 tokens.
- Arquivos: este registro, índice e planning se afetado (até três).
- Identificar consumidor/pergunta de negócio e propor agregação concreta; confirmar
  granularidade, métricas, filtros, schema, namespace, recorte e idempotência.
  Registrar escolha do usuário quando houver alternativas de negócio relevantes.
- Definir tabelas Prata de origem, tabela Ouro destino, recorte pequeno porém real
  para reprodução, critérios de resultado e consulta SQL de consumo.
- Evidência: contrato preenchido aqui. Se faltar definição de negócio, bloquear
  apenas a implementação Ouro; não inventar métrica nem bloquear setup da stack.
- Resultado: pendente.

### E02 — Implementar publicação Ouro

- Status: backlog; depende de E01 e TASK-0006; estimativa: 4.000 tokens.
- Arquivos: `ouro.py` no pipeline escolhido, `info.py` se necessário,
  `orquestrador.py` + controle (cinco).
- Implementar transformação DuckDB a partir da Prata, publicação transacional pelo
  Polaris no RustFS, recorte idempotente e falha propagada. Se precisar alterar utils,
  deployment ou outros arquivos, desdobrar nova etapa antes do limite.
- Evidência: entrega pronta para flow completo, sem validações isoladas como aceite.
- Resultado: pendente.

### E03 — Flow completo e consulta real

- Status: backlog; depende de E02 e TASK-0008; estimativa: 4.500 tokens.
- Arquivos: tarefa/índice e até três correções de escopo (até cinco).
- Executar flow completo Bronze → Prata → Ouro pelo ambiente/perfil debug do projeto
  até Completed, depois pelo deployment. Consultar Ouro no Trino como consumidor.
- Repetir recorte sem duplicação, comparar métricas/contagens às origens, comprovar
  visibilidade de novo snapshot, reiniciar serviços e consultar novamente.
- Com o mesmo consumidor, comprovar negação de leitura Prata/Bronze e de escrita,
  DDL e procedures mutáveis; usar tabela/recorte dedicado para tentativas que poderiam
  escrever se a configuração estiver errada. Não testar destruição em tabelas de negócio.
- Registrar comandos/perfis, parâmetros, run IDs, estados, consultas, resultados e
  negações sem segredos. Falhou: erro, causa provável, menor correção e repetir flow.
- Resultado: pendente; impedimento de ambiente mantém aceite pendente.

### E04 — Documentar e encerrar arquitetura nova

- Status: backlog; depende de E03; estimativa: 3.000 tokens.
- Arquivos: `README.md`, planning, `.env.example` quando afetado + controle (cinco).
- Documentar setup do zero, conexão SQL, autenticação, tabela Ouro e permissões,
  recursos e limitações. Conferir nenhuma configuração padrão depende de MinIO ou
  Lakekeeper; referências históricas e SDK cliente podem permanecer explicadas.
- Registrar evidências e QA final; atualizar grafo após código, dividindo saídas
  geradas em etapa própria se necessário para respeitar cinco arquivos.
- Resultado: pendente.

## Aceite e retomada

E02 implementada: `PipeOuro` filtra ano na Prata, valida campos obrigatórios,
agrega com DECIMAL, reconcilia soma/quantidade e publica partição anual pelo Polaris.
Orquestrador de despesas inclui Ouro. Critério E03 pendente de engine Docker;
nenhum resultado financeiro ou run foi declarado validado. Antecipada implementação
para avançar enquanto ambiente está bloqueado; dependências executáveis permanecem.

- [ ] Produto Ouro definido com necessidade real e contrato explícito.
- [ ] Flow completo publica e reprocessa sem duplicação; snapshot novo visível no Trino.
- [ ] Consumidor lê Ouro, sem ler camadas internas ou modificar dados.
- [ ] Reinicialização e documentação comprovam ambiente novo independente do legado.
- Próxima ação: E01 após TASK-0003; implementação pendente de negócio e TASK-0006.
- 2026-11-03 — tarefa criada para fechar entrega ponta a ponta da arquitetura aprovada.
