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

## Credenciais
Por solicitação explícita, Prefect/DuckDB usam a chave administrativa do RustFS para
leitura e escrita dos flows. ClickHouse deve usar identidade IAM distinta, somente
leitura do prefixo `iceberg/nessie-warehouse/`, para acessar metadados e arquivos
Iceberg. Chaves e senhas ficam apenas no `.env`; política declarativa pode ser versionada.

## Riscos/decisões
DuckDB exige REST catalog para escrever Iceberg. REST do Nessie é experimental.
ClickHouse lista tabelas Nessie, mas sua leitura retorna HTTP 403 do RustFS mesmo
com `storage_endpoint` configurado e a mesma credencial validada por DuckDB e pela
função `s3()` do ClickHouse. A causa corresponde ao problema aberto
[ClickHouse #111529](https://github.com/ClickHouse/ClickHouse/issues/111529): o
`DataLakeCatalog` não propaga as credenciais S3 para os engines Iceberg subjacentes.
O endpoint Nessie local não tem autenticação e está publicado apenas em loopback.

Para a navegação JDBC, o perfil `readonly` habilita
`show_data_lake_catalogs_in_system_tables`. Após reiniciar ClickHouse, `analista`
encontrou a tabela e suas quatro colunas em `system.tables` e `system.columns`;
falta confirmar a atualização visual no DBeaver. Isso resolve a descoberta dos
metadados pelo cliente, mas não a leitura dos arquivos Iceberg pelo catálogo.

Leitura direta via `icebergS3('http://rustfs:9000/<bucket>/<local-da-tabela>/')`
foi validada na tabela Iceberg de Legislaturas: 57 linhas, IDs de 1 a 57. A função
foi executada com `lakehouse_admin`; `analista` foi barrado por `readonly=1` antes
da leitura. Criar uma tabela nomeada com engine `IcebergS3` falhou com
`Table cannot have empty namespace`. A função direta é uma alternativa diagnóstica,
mas ainda não fornece consumo por nome para usuário somente leitura nem descoberta
automática via Nessie.

A identidade IAM RustFS `clickhouse_iceberg_ro` agora usa política customizada
restrita a `iceberg/nessie-warehouse/`: `GetBucketLocation`, `ListBucket` somente
nesse prefixo e `GetObject`. A consulta ClickHouse direta retornou 57 linhas com
essa credencial; listagem foi permitida e tentativa de escrita foi negada. O worker
recebe as credenciais administrativas conforme pedido, enquanto o Prefect Server
não recebe credenciais S3. O usuário SQL `analista` segue com `readonly=1`.

## Aceite
Aceitos: Compose valida, Nessie fica saudável, DuckDB anexa o catálogo REST e o flow
Legislaturas conclui com 57 registros e snapshot Iceberg `1579976123849263804` no
warehouse novo `nessie-warehouse`. ClickHouse fica saudável, autentica o cliente e
lista a tabela, mas a leitura SQL via `DataLakeCatalog` falha com código 499/HTTP 403.
A leitura direta via `icebergS3()` recupera os 57 registros pelo path Iceberg usando
a identidade IAM somente leitura do ClickHouse. A leitura via `DataLakeCatalog`
segue falhando com HTTP 403 e `analista` não pode executar a table function em
`readonly=1`; acesso SQL de consumidor por nome permanece bloqueado.

Os containers antigos Polaris/PostgreSQL/Trino e bootstraps foram removidos; os
volumes `polaris-db-data` e `rustfs-data` continuam intactos. Nenhum `down -v` foi
executado. Arquivos versionados e referências operacionais obsoletas foram removidos.
