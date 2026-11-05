# TASK-0025 — Trocar Polaris/Trino por Nessie/ClickHouse

- Status: bloqueada
- Categoria: infraestrutura
- Tipo: melhoria
- Prioridade: P1
- Origem: pedido explícito do usuário, 2026-11-05.

## Contrato
Manter Iceberg, DuckDB, RustFS e Prefect; remover Polaris, PostgreSQL e Trino.
Nessie fornece catálogo REST e estado persistente; ClickHouse serve SQL de leitura
das tabelas Iceberg no RustFS. Preservar volumes existentes e credenciais sem
apagá-los nem migrar catálogos implicitamente. Warehouse novo isolado no mesmo bucket.
Usuário confirmou uso de Nessie.

## Riscos/decisões
DuckDB exige REST catalog para escrever Iceberg. REST do Nessie é experimental.
ClickHouse lista tabelas Nessie, mas sua leitura retorna HTTP 403 do RustFS mesmo
com `storage_endpoint` configurado e a mesma credencial validada por DuckDB e pela
função `s3()` do ClickHouse. A causa corresponde ao problema aberto
[ClickHouse #111529](https://github.com/ClickHouse/ClickHouse/issues/111529): o
`DataLakeCatalog` não propaga as credenciais S3 para os engines Iceberg subjacentes.
O endpoint Nessie local não tem autenticação e está publicado apenas em loopback.

Leitura direta via `icebergS3('http://rustfs:9000/<bucket>/<local-da-tabela>/')`
foi validada na tabela Iceberg de Legislaturas: 57 linhas, IDs de 1 a 57. A função
foi executada com `lakehouse_admin`; `analista` foi barrado por `readonly=1` antes
da leitura. Criar uma tabela nomeada com engine `IcebergS3` falhou com
`Table cannot have empty namespace`. A função direta é uma alternativa diagnóstica,
mas ainda não fornece consumo por nome para usuário somente leitura nem descoberta
automática via Nessie.

## Aceite
Aceitos: Compose valida, Nessie fica saudável, DuckDB anexa o catálogo REST e o flow
Legislaturas conclui com 57 registros e snapshot Iceberg `1579976123849263804` no
warehouse novo `nessie-warehouse`. ClickHouse fica saudável, autentica o cliente e
lista a tabela, mas a leitura SQL via `DataLakeCatalog` falha com código 499/HTTP 403.
A leitura direta via `icebergS3()` recupera os 57 registros pelo path Iceberg, mas
somente com usuário administrativo; acesso de consumidor e descoberta por nome
permanecem bloqueados até definir uma exposição segura das tabelas.

Os containers antigos Polaris/PostgreSQL/Trino e bootstraps foram removidos; os
volumes `polaris-db-data` e `rustfs-data` continuam intactos. Nenhum `down -v` foi
executado. Arquivos versionados e referências operacionais obsoletas foram removidos.
