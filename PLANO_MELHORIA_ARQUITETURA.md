# Plano de melhoria da arquitetura de dados

## 1. Objetivo

Evoluir a plataforma Prefect + DuckDB + MinIO para processar com segurança:

- poucos arquivos e execução local;
- milhões de objetos pequenos;
- arquivos individuais com vários GB;
- múltiplos flows simultâneos;
- vários produtores e consumidores concorrentes no MinIO;
- reprocessamentos sem duplicação ou perda de dados.

## 2. Avaliação atual

### Pontos positivos

- Separação clara por projeto, pipeline e camadas bronze/prata/ouro.
- Prefect fornece observabilidade, retries, agendamento e dependências entre etapas.
- DuckDB é simples, rápido e eficiente para transformação analítica em uma única máquina.
- MinIO desacopla armazenamento e processamento e mantém compatibilidade com S3.
- Schemas centralizados em `info.py` facilitam padronização inicial.
- Parquet na camada prata reduz leitura, armazenamento e tráfego em comparação com JSON/CSV.

### Limitações e riscos

1. `_read_dataframe` lista todos os objetos e cria uma tabela temporária por arquivo. O custo de memória, catálogo e planejamento SQL cresce linearmente com a quantidade de arquivos.
2. `_read_arquivo` e partes da extração usam `BytesIO`, mantendo arquivos inteiros em RAM. Um arquivo de vários GB pode encerrar o worker por falta de memória.
3. A união final materializa os dados novamente no DuckDB. O pico pode envolver dados de entrada, tabelas temporárias e tabela final ao mesmo tempo.
4. O DuckDB está em memória e não possui limites explícitos de memória, threads ou diretório temporário.
5. Escritas usam nomes finais diretamente e podem apagar dados antes de uma nova versão estar completa. Falhas no meio da execução podem deixar partições vazias ou incompletas.
6. Não há manifesto de execução, checksum, watermark ou controle formal de idempotência.
7. Dois flows podem escrever no mesmo prefixo simultaneamente, produzindo condição de corrida e resultado não determinístico.
8. O worker possui concorrência 20, mas não existem limites separados por CPU, memória, API externa ou MinIO.
9. O MinIO está em instância única e volume local único. Isso é adequado para desenvolvimento, mas não fornece alta disponibilidade nem tolerância à perda do disco.
10. Todos os processos usam credenciais administrativas compartilhadas, sem políticas específicas por pipeline ou camada.
11. Muitos JSONs pequenos aumentam latência de listagem, chamadas HTTP, metadados e custo de abertura de arquivos.
12. A instalação de extensões DuckDB durante a criação de cada conexão depende de rede e adiciona latência e um ponto de falha.
13. O Prefect usa armazenamento local no compose; em produção, o servidor e seu estado precisam de banco persistente e backup.
14. Logs e erros não registram métricas padronizadas de volume, duração, throughput, memória, tentativas e arquivos rejeitados.

## 3. Arquitetura recomendada

### 3.1 Contrato de armazenamento

Adotar paths imutáveis e particionados:

```text
bronze/{projeto}/{pipeline}/ano=YYYY/mes=MM/dia=DD/run_id={id}/part-*.json
prata/{projeto}/{pipeline}/ano=YYYY/mes=MM/data-*.parquet
quarentena/{projeto}/{pipeline}/run_id={id}/...
```

Regras:

- Bronze é append-only: nunca apagar ou sobrescrever dados de uma execução anterior.
- Cada execução escreve primeiro em `_staging/run_id={id}`.
- Publicar os dados somente após validação completa, por commit de metadados ou movimentação controlada do prefixo.
- Criar um manifesto por execução contendo arquivos, tamanhos, ETags/checksums, schema, quantidade de registros, origem, timestamps e status.
- A chave de idempotência deve combinar pipeline, partição lógica e parâmetros da execução.
- Reprocessamentos geram nova versão; não alteram silenciosamente uma versão já publicada.

### 3.2 Leitura e transformação

Substituir a tabela temporária por arquivo por leitura vetorizada em lote:

- Para arquivos homogêneos, passar uma lista de paths ou glob diretamente a `read_json_auto`, `read_csv_auto` ou `read_parquet`.
- Usar `union_by_name=true` quando apropriado.
- Validar o schema com metadados/amostras antes da materialização completa.
- Processar formatos diferentes em grupos por extensão, não individualmente.
- Unir poucos grupos de leitura, em vez de milhares de tabelas temporárias.
- Projetar somente colunas necessárias e aplicar filtros de partição na origem.
- Para arquivos gigantes, fazer leitura streaming/chunked ou deixar o DuckDB ler diretamente do S3; nunca converter todo o arquivo para `bytes` ou `BytesIO`.
- Configurar `memory_limit`, `threads`, `temp_directory` e `max_temp_directory_size` por worker.
- Usar banco DuckDB temporário em disco para cargas maiores que a memória disponível.
- Definir limite de arquivos e bytes por lote; criar múltiplas tasks quando o limite for excedido.

Configuração inicial sugerida por worker:

```sql
SET memory_limit = '60%';
SET threads = 4;
SET temp_directory = '/var/lib/pipeline/tmp';
SET preserve_insertion_order = false;
```

Os valores devem ser parametrizados conforme CPU e memória do ambiente.

### 3.3 Formato e compactação

- Converter JSON/CSV bronze para Parquet o mais cedo possível.
- Usar compressão ZSTD e row groups entre 64 MB e 256 MB.
- Buscar arquivos Parquet finais entre 128 MB e 1 GB; evitar tanto arquivos minúsculos quanto arquivos únicos enormes.
- Criar uma rotina de compactação para partições com muitos arquivos pequenos.
- Particionar apenas por colunas usadas com frequência em filtros e com cardinalidade baixa/moderada, como ano e mês.
- Não particionar por identificadores de alta cardinalidade, como deputado ou documento.
- Ordenar dentro do Parquet por colunas de filtros comuns quando isso melhorar pruning.

### 3.4 Schema e qualidade

- Mover schemas para modelos tipados/versionados, com versão registrada no manifesto.
- Separar validação de presença, conversão de tipo e regras de negócio.
- Validar todos os arquivos antes de publicar a partição.
- Enviar arquivos inválidos à quarentena, mantendo nome, erro, schema esperado e run ID.
- Definir política explícita para colunas extras, ausentes, nulas e casts inválidos.
- Usar `TRY_CAST` somente quando houver regra para tratar os valores rejeitados; não ocultar erros silenciosamente.
- Registrar contagens de entrada, saída, rejeitados, duplicados e nulos por coluna crítica.

### 3.5 Concorrência e Prefect

- Criar work pools separados por perfil: `io-small`, `cpu-transform` e `large-files`.
- Aplicar limites de concorrência por recurso, não apenas um limite global.
- Usar uma chave de concorrência por partição, por exemplo `deputados-prata-2026`, impedindo duas escritas simultâneas no mesmo destino.
- Permitir paralelismo entre anos/partições diferentes.
- Configurar retries com exponential backoff e jitter para API e MinIO.
- Definir timeout por task e cancelamento seguro.
- Não compartilhar uma conexão DuckDB entre tasks ou threads. Cada task deve possuir conexão e diretório temporário próprios.
- Aplicar limites menores para tasks de arquivos grandes, considerando memória reservada por execução.
- Persistir resultados intermediários somente quando necessário; preferir referências a objetos no MinIO em vez de bytes no estado do Prefect.

Exemplo de capacidade:

| Perfil | Concorrência inicial | Uso esperado |
|---|---:|---|
| `io-small` | 8–16 | Downloads e uploads pequenos |
| `cpu-transform` | 2–4 | Conversão e compactação Parquet |
| `large-files` | 1 | Arquivos com vários GB |

Esses números são ponto de partida e devem ser ajustados por métricas de CPU, RAM, disco e rede.

### 3.6 MinIO

Para desenvolvimento e pequena escala:

- Manter instância única, mas habilitar versionamento, lifecycle e backups.
- Criar usuários e policies por ambiente e por função.
- Separar credenciais de leitura da bronze e escrita da prata.

Para produção e grande escala:

- Executar MinIO distribuído com múltiplos nós e discos, erasure coding e volumes dedicados.
- Usar rede e discos dimensionados para o throughput simultâneo esperado.
- Habilitar métricas Prometheus, alertas, auditoria e verificação periódica de integridade.
- Configurar lifecycle para staging abandonado, versões antigas e retenção da bronze.
- Avaliar replicação para outro cluster/site e testes regulares de restauração.
- Evitar listagens recursivas amplas; consultar prefixos de partição específicos ou manifestos.
- Monitorar latência, erros 4xx/5xx, throughput, quantidade de objetos, espaço livre e tempo de healing.

### 3.7 Catálogo e transações

Quando houver múltiplos escritores/leitores, evolução de schema ou necessidade de snapshots, adotar Apache Iceberg de forma efetiva:

- Usar um catálogo persistente compatível, em vez de apenas carregar a extensão DuckDB.
- Publicar commits atômicos e snapshots.
- Usar optimistic concurrency control para escritores concorrentes.
- Executar manutenção de snapshots, manifests e arquivos órfãos.
- Permitir time travel e rollback de versões.

Parquet simples permanece suficiente para cargas pequenas, um único escritor por partição e baixa necessidade de evolução transacional.

### 3.8 Segurança e configuração

- Validar variáveis de ambiente na inicialização e falhar com mensagem clara.
- Armazenar segredos em Prefect Blocks/Secrets ou secret manager; não usar credenciais root nos flows.
- Habilitar TLS entre workers e MinIO em produção.
- Fixar versões das imagens Docker; evitar tags `latest`.
- Pré-instalar extensões DuckDB na imagem ou em diretório persistente e carregar sem `INSTALL` a cada conexão.
- Executar containers com usuário não root e filesystem temporário controlado.
- Separar configurações de desenvolvimento, homologação e produção.

### 3.9 Observabilidade

Registrar por task e partição:

- run ID e versão do código;
- arquivos e bytes lidos/escritos;
- registros de entrada, saída e quarentena;
- duração, throughput, retries e status;
- memória máxima, uso do diretório temporário e CPU;
- schema e partição publicados;
- ETags/checksums e manifesto gerado.

Criar alertas para:

- falha ou atraso de flow;
- divergência de contagem;
- crescimento inesperado de nulos ou rejeitados;
- pouco espaço em disco/MinIO;
- latência e taxa de erro elevadas;
- excesso de arquivos pequenos;
- staging antigo sem commit.

## 4. Cenários operacionais

### Pequena escala

DuckDB em memória e MinIO único são suficientes quando o volume cabe confortavelmente em RAM/disco, existe um escritor por partição e a indisponibilidade local é aceitável. Mesmo nesse cenário, implementar escrita em staging, idempotência, manifestos e limites de concorrência.

### Muitos arquivos pequenos

O gargalo principal será metadado e abertura de objetos, não CPU. Agrupar leituras por formato, evitar `list_objects` amplo, compactar periodicamente e consumir a partir de manifestos. Não criar uma tabela DuckDB por arquivo.

### Arquivos com vários GB

Não usar `BytesIO`. Fazer multipart upload e leitura direta S3/streaming. Reservar worker exclusivo, limitar memória, habilitar spill para SSD e produzir múltiplos Parquets de tamanho controlado.

### Muitos flows simultâneos

Aplicar concorrência por recurso e lock por partição. Isolar diretórios temporários e conexões. Dimensionar o número de workers pela memória, não somente por CPU. Um limite global de 20 processos pode ser perigoso se cada DuckDB consumir vários GB.

### Muitos dispositivos lendo e escrevendo no MinIO

Usar objetos imutáveis, publicação atômica por metadados e credenciais específicas. Leitores devem consumir somente versões marcadas como completas. Escalar MinIO horizontalmente e monitorar rede, discos e filas de requests.

## 5. Plano de implementação

### Fase 0 — Medição e critérios

- [ ] Definir volumes atuais e projetados: arquivos/dia, bytes/dia, tamanho máximo e retenção.
- [ ] Definir SLOs de duração, disponibilidade, recuperação e perda aceitável de dados.
- [ ] Criar benchmark com 10 mil arquivos pequenos, arquivo de 10 GB e quatro flows simultâneos.
- [ ] Medir baseline de RAM, CPU, disco temporário, requests MinIO e duração.

Critério de conclusão: baseline reproduzível e limites operacionais documentados.

### Fase 1 — Segurança e idempotência

- [ ] Adicionar run ID e paths de staging.
- [ ] Publicar manifesto e marcador de sucesso somente após validação.
- [ ] Remover exclusão antes da escrita e tornar bronze append-only.
- [ ] Implementar chave idempotente e lock/concurrency limit por partição.
- [ ] Adicionar retries, timeout e backoff para API/MinIO.
- [ ] Implementar quarentena e limpeza automática de staging abandonado.

Critério de conclusão: uma falha ou reexecução não perde, duplica nem expõe dados parciais.

### Fase 2 — Memória e grandes arquivos

- [ ] Remover `BytesIO` de caminhos de dados grandes.
- [ ] Implementar upload multipart e streams seekable quando necessário.
- [ ] Configurar DuckDB com limites de memória, threads e spill em disco.
- [ ] Isolar diretório temporário por run/task.
- [ ] Ler diretamente do MinIO e escrever Parquet em partes controladas.
- [ ] Criar testes de carga para arquivo maior que a RAM do worker.

Critério de conclusão: processar arquivo maior que a RAM sem encerramento do worker.

### Fase 3 — Muitos arquivos

- [ ] Agrupar objetos por formato e executar uma leitura DuckDB por grupo/lote.
- [ ] Substituir listagens amplas por manifestos e prefixes particionados.
- [ ] Implementar tamanho máximo de lote por quantidade e bytes.
- [ ] Adicionar compactação automática de pequenos Parquets.
- [ ] Coletar métricas de quantidade e tamanho médio dos objetos.

Critério de conclusão: processar 10 mil arquivos sem criar 10 mil tabelas temporárias e com memória limitada.

### Fase 4 — Concorrência e infraestrutura

- [ ] Criar work pools por perfil de carga.
- [ ] Dimensionar concorrência com base em RAM reservada por task.
- [ ] Migrar o backend do Prefect para banco persistente com backup.
- [ ] Fixar imagens e pré-instalar dependências/extensões.
- [ ] Criar policies MinIO de menor privilégio e habilitar TLS.
- [ ] Implantar dashboards e alertas.

Critério de conclusão: flows concorrentes em partições diferentes não interferem; a mesma partição possui exclusão mútua.

### Fase 5 — Escala distribuída e governança

- [ ] Implantar MinIO distribuído e testar falha de nó/disco.
- [ ] Adotar catálogo Iceberg quando houver múltiplos escritores ou necessidade de snapshots.
- [ ] Implementar manutenção de snapshots, manifests e arquivos órfãos.
- [ ] Testar restore, replicação e disaster recovery.
- [ ] Versionar contratos de schema e definir política de evolução.

Critério de conclusão: publicação transacional, recuperação testada e tolerância à falha definida pelo SLO.

## 6. Ordem de prioridade

1. Escrita segura, idempotência e lock por partição.
2. Eliminação de `BytesIO` e limites explícitos do DuckDB.
3. Leitura em lote e compactação de arquivos pequenos.
4. Observabilidade e work pools dimensionados por recurso.
5. MinIO distribuído e catálogo Iceberg quando a escala justificar.

## 7. Decisão prática

Não migrar imediatamente para Spark ou outra engine distribuída. Primeiro otimizar o desenho com DuckDB, particionamento, batches, spill e workers isolados. Considerar engine distribuída somente quando uma única partição precisar ser processada em paralelo por várias máquinas, o SLA não puder ser atendido por scale-up, ou o volume ultrapassar de forma recorrente a capacidade de disco e memória de um worker dimensionado.
