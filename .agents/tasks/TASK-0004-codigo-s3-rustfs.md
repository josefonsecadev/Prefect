# TASK-0004 — Adaptar acesso aos dados para RustFS

## Identificação

- Status: backlog
- Categoria: dados
- Tipo: melhoria
- Etiquetas: [rustfs, s3, python, duckdb, bronze, prata]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: migração aprovada para RustFS, mantendo contratos dos pipelines.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: TASK-0003 concluída.

## Objetivo e contexto

Configurar o acesso compartilhado S3 para RustFS sem alterar regras de negócio,
schemas, caminhos, partições, parâmetros públicos ou resultados dos pipelines.
Usar Engenharia de Dados após contratos definidos. Configuração atual exige
MINIO_* e `Conexoes._minio()` é usada em `utils/pipeline.py`. DuckDB configura seu
próprio cliente S3; ambos devem compartilhar endpoint, credenciais, região e TLS.

Referências: `utils/config.py`, `utils/conexoes.py`, `utils/pipeline.py`,
`.env.example`, `.vscode/launch.json`, `pyproject.toml`, `poetry.lock`.
SDK MinIO pode permanecer como cliente S3 conforme TASK-0003; retirar o servidor
não exige substituir a biblioteca. Não atualizar Prefect/DuckDB/dependências sem necessidade.

## Etapas

Reservar em cada etapa este arquivo e índice, além dos arquivos listados.
Estimativas incluem contexto e revisão; dividir se ultrapassar 5.000 tokens ou
cinco arquivos. Não criar testes, mocks ou simulações; aceite executável em TASK-0006.

### E01 — Configuração S3 e conexão DuckDB

- Status: backlog.
- Estimativa: 4.000 tokens.
- Arquivos: `utils/config.py`, `utils/conexoes.py`, `.env.example` + controle (cinco).
- Ações: implementar contrato S3 da TASK-0003, validação de variáveis sem expor
  credenciais, parsing correto de TLS/região e endpoint, DuckDB configurado no
  mesmo storage. Usar nomes genéricos S3 em atributos novos, migrando referências.
- Preservar temporariamente `_minio()` como adaptador para os chamadores existentes
  até E02. Não deixar atributos removidos referenciados nesse adaptador.
- Evidência: revisão de chamadas e diff; validação completa adiada para TASK-0006.
- Resultado: pendente.

### E02 — Chamadores e debug local

- Status: backlog; depende de E01.
- Estimativa: 3.500 tokens.
- Arquivos: `utils/pipeline.py`, `utils/conexoes.py`, `.vscode/launch.json` + controle (cinco).
- Ações: migrar chamadas do adaptador para abstração S3; preservar listagem paginada,
  PUT/multipart, GET, fechamento de resposta e exclusão apenas no recorte previsto.
  Ajustar debug dos três flows para endpoints do host; preservar endpoints internos
  dos containers. Não renomear tabelas, buckets nem arquivos das fontes.
- Evidência: nenhuma referência quebrada aos atributos/métodos migrados; perfis
  de debug coerentes; sem execução isolada como substituto do flow.
- Resultado: pendente.

## Critérios de aceite

- [ ] Código usa contrato S3 explícito com RustFS como padrão nos exemplos.
- [ ] DuckDB e cliente Python usam as mesmas configurações de armazenamento.
- [ ] Chamadores e debug ajustados; negócio e contratos dos flows preservados.
- [ ] Diff revisado e entrega pronta para integração em TASK-0005/0006.

## Retomada e histórico

- Próxima ação: ler contratos fechados em TASK-0003 e iniciar E01.
- Feito: somente planejamento; nada implementado.
- Bloqueios: dependência de contratos; eventual troca de SDK exige replanejamento.
- Validação pendente: todos os flows completos e idempotência em TASK-0006.
- 2026-11-03 — tarefa registrada; estimativas não representam tokens medidos.
