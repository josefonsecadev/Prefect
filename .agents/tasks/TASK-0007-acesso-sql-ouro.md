# TASK-0007 — Planejar camada SQL de acesso à Ouro

## Identificação

- Status: pronta
- Categoria: infraestrutura
- Tipo: investigacao
- Etiquetas: [ouro, sql, trino, apache, iceberg, lakekeeper, rustfs, seguranca, bi]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário solicitou camada de acesso à Ouro, sugeriu Trino e aceita alternativas, principalmente Apache.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: pesquisa pode iniciar agora; integração/implantação futura depende de TASK-0006.

## Objetivo e contexto

Definir uma engine de consulta SQL para dashboards, aplicações e usuários acessarem
somente a Ouro, com acesso de leitura e sem receber credenciais do armazenamento.
É uma camada de acesso/serving sobre a Ouro existente; não é uma nova camada medalhão.
Preservar Prefect, DuckDB como transformação, Iceberg, catálogo Lakekeeper e RustFS.
Não substituir o catálogo nem introduzir cópia dos dados para outra base sem decisão explícita.

Usar Arquitetura de Software e apresentar benefícios/custos antes de escolher.
Trino é candidato preferencial do usuário, não escolha aprovada. Distinguir licença
Apache-2.0 de pertencer à Apache Software Foundation; verificar ambos para cada opção.

Referências locais: `README.md` (consumo somente Ouro), `.agents/knowledge/planning.md`,
`docker-compose.yml`, `prefect.yaml`, TASK-0003 a TASK-0006.
Inspeção anterior identificou flows Bronze/Prata, sem produto Ouro confirmado.
Não apresentar Prata como Ouro para viabilizar uma demonstração. Confirmar tabelas
Ouro e contratos de consumo; se ausentes, criar tarefa dependente para o primeiro
produto Ouro após definição de métricas e necessidade real, sem inventar regras.

## Candidatos e fontes iniciais

- [Trino: conector Iceberg](https://trino.io/docs/current/connector/iceberg.html):
  avaliar REST Catalog, acesso S3 nativo, autorização por schema/tabela e clientes BI/JDBC.
- [Apache Doris: integração Lakekeeper](https://doris.apache.org/docs/3.x/lakehouse/best-practices/doris-lakekeeper/):
  avaliar catálogo externo Iceberg, permissões, recursos e complexidade FE/BE.
- [Apache Spark SQL: consultas Iceberg](https://iceberg.apache.org/docs/latest/spark-queries/):
  avaliar acesso SQL/JDBC e adequação ao consumo interativo versus processamento batch.
- DuckDB atual é referência de custo/simplicidade; confirmar se atende a acesso
  multiusuário antes de propor novo serviço. Não presumir equivalência de servidor SQL.

Fontes são ponto de partida, não comprovação de integração nas versões escolhidas.
Não pontuar desempenho sem workload ou medição. Avaliar versões, licença, projeto
responsável, maturidade, manutenção, RAM/CPU, concorrência, latência, observabilidade,
compatibilidade Iceberg (incluindo deletes/snapshots), Lakekeeper e S3 RustFS.

## Etapas

Estimativas incluem pesquisa, revisão e manutenção do controle. Cada etapa altera
no máximo cinco arquivos, incluindo tarefa/índice; dividir antes de exceder 5.000 tokens.
Esta tarefa não autoriza implantação nem mudanças em produção.

### E01 — Requisitos e comparação

- Status: pronta.
- Estimativa: 4.000 tokens.
- Arquivos: este registro e índice (dois).
- Ações: identificar consumidor inicial (BI, aplicação ou analista), ferramenta e
  protocolo exigidos, volume Ouro, frequência de atualização, simultaneidade,
  latência esperada, RAM/CPU e autenticação. Verificar existência de Ouro e se
  preferência Apache significa ASF ou licença permissiva.
- Produzir matriz de alternativas e recomendação fundamentada para a stack atual.
  Separar fatos verificados, premissas e dúvidas que alteram a decisão.
- Evidência esperada: fontes oficiais, matriz, requisitos e opções apresentados ao usuário.
- Resultado: pendente; nenhuma engine escolhida.

### E02 — Escolha conjunta e contrato de acesso

- Status: backlog; depende de E01 e escolha do usuário.
- Estimativa: 3.500 tokens.
- Arquivos: este registro, índice, `.agents/knowledge/planning.md` (três).
- Ações: registrar engine e versão escolhidas; definir topologia Docker, conector
  REST Lakekeeper, storage RustFS, portas, TLS/autenticação, permissões e orçamento
  de recursos. Credenciais de serviço ficam no backend, não com consumidores.
- Contrato obrigatório: permitir apenas SELECT/metadata autorizados da Ouro;
  impedir leitura de Bronze/Prata e INSERT/UPDATE/DELETE/DDL e procedures de escrita.
  Modo read-only global sozinho não restringe namespaces; definir autorização por
  schema/tabela, funções/procedures e acessos alternativos a arquivos/catálogos.
- Definir atualização/visibilidade de snapshots, limites/timeouts de consultas,
  logs sem dados sensíveis, falhas e recuperação; não prometer HA com nó único.
- Evidência: arquitetura aprovada e critérios verificáveis; não instalar ainda.
- Resultado: pendente.

### E03 — Criar tarefas implementáveis da solução escolhida

- Status: backlog; depende de E02; implantação depende de TASK-0006 e produto Ouro disponível.
- Estimativa: 2.500 tokens.
- Arquivos: este registro, índice e até três novas tarefas (até cinco).
- Desdobrar: implantação/conectores, autorização/acesso do consumidor e validação
  ponta a ponta/documentação. Se precisar de mais tarefas, criar outra etapa.
- Aceite futuro: consumidor real consulta tabela Ouro produzida por flow completo;
  resultado confere com origem; nova execução fica visível; leitura de Bronze/Prata
  e operações de escrita são negadas; indisponibilidade e reinicialização verificadas.
- Não criar testes, mocks ou scripts de simulação para substituir execução de flows.
- Resultado: pendente.

## Critérios de aceite e retomada

- [ ] Requisitos e existência de tabelas Ouro confirmados; comparação oficial registrada.
- [ ] Engine escolhida pelo usuário, com justificativa e contrato somente leitura/Ouro.
- [ ] Tarefas de implantação pequenas criadas, com dependências e validação concreta.
- Próxima ação: E01; executar pesquisa sem depender da migração, implantar após TASK-0006.
- Bloqueios futuros: escolha da engine e eventual ausência de produto Ouro.
- Feito: apenas registro da demanda; Trino não foi instalado ou aprovado como padrão.
- 2026-11-03 — tarefa registrada durante planejamento da migração RustFS.
