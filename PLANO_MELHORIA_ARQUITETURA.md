# Plano de melhoria da arquitetura

Este plano contém somente problemas arquiteturais identificados, o impacto de mantê-los e a arquitetura que deve substituí-los. Regras e implementações específicas de datasets não fazem parte deste documento.

## 1. Publicação da Bronze sem contrato transacional

**O que está ruim:** objetos da Bronze são gravados em caminhos finais e podem ser removidos antes da nova escrita. Não existe manifesto, versão publicada nem distinção formal entre uma carga completa e uma carga interrompida.

**Por que precisa mudar:** uma falha durante a escrita pode remover a versão anterior ou deixar um conjunto parcial disponível. Também não há rastreabilidade suficiente para determinar quais objetos formaram uma publicação.

**Substituir por:** armazenamento imutável por execução, seguido de publicação por metadados.

```text
bronze/{dominio}/{dataset}/{particao}/run_id={id}/part-*
bronze/{dominio}/{dataset}/{particao}/run_id={id}/manifest.json
bronze/{dominio}/{dataset}/{particao}/_published.json
quarentena/{dominio}/{dataset}/{particao}/run_id={id}/...
```

O manifesto deve registrar arquivos, tamanhos, checksums, parâmetros, schema, contagens e status. O marcador `_published.json` deve apontar somente para uma execução validada. Limpeza e retenção devem ocorrer fora do caminho de publicação.

**Critério de aceite:** uma falha antes da publicação mantém a versão anterior disponível; leitores nunca encontram uma versão parcial; cada publicação é rastreável até seus objetos e parâmetros.

## 2. Idempotência e concorrência sem coordenação por partição

**O que está ruim:** existe apenas um limite global de concorrência. Execuções que publicam na mesma partição lógica não possuem exclusão mútua, enquanto cargas com perfis diferentes disputam a mesma capacidade.

**Por que precisa mudar:** escritores concorrentes podem gerar conflitos ou resultados não determinísticos. Um limite global também permite que cargas pesadas esgotem recursos necessários às demais.

**Substituir por:** chave operacional `(dataset, partição lógica)`, limites de concorrência por perfil de recurso e lock de publicação por chave. O Iceberg deve continuar como fronteira transacional e rejeitar conflitos inesperados.

Perfis mínimos:

- I/O leve;
- transformação intensiva em CPU;
- arquivos grandes e alto consumo de memória.

**Critério de aceite:** duas execuções da mesma chave não publicam simultaneamente; chaves distintas podem avançar em paralelo; conflitos nunca são resolvidos por sobrescrita silenciosa.

## 3. Processamento sem orçamento de recursos

**O que está ruim:** DuckDB opera em memória sem limites explícitos de memória, threads, spill ou armazenamento temporário. A concorrência do worker não considera o consumo máximo de cada execução.

**Por que precisa mudar:** uma única carga pode consumir toda a memória ou o disco do worker. Com concorrência elevada, o risco é multiplicado e pode indisponibilizar todas as execuções no mesmo host.

**Substituir por:** perfis de execução com `memory_limit`, `threads`, `temp_directory`, limite de spill, limite de lote e diretório temporário exclusivo. O número de execuções simultâneas deve ser calculado pelo orçamento de memória:

```text
concorrência máxima x memória máxima por execução < memória útil do worker
```

**Critério de aceite:** nenhuma execução ultrapassa o orçamento definido; spill não disputa o mesmo diretório entre execuções; falta de recurso encerra somente a carga afetada e produz diagnóstico operacional.

## 4. Estratégia de leitura que não escala com volume

**O que está ruim:** a leitura cria uma tabela temporária por objeto e materializa arquivos grandes integralmente em memória em partes do caminho de dados. Listagens recursivas amplas são usadas para descobrir entradas.

**Por que precisa mudar:** o custo de catálogo e planejamento cresce linearmente com a quantidade de objetos. Arquivos maiores que a memória disponível podem encerrar o worker, e listagens amplas degradam conforme o armazenamento cresce.

**Substituir por:** leitura vetorizada em lotes, consumo orientado por manifestos, streaming de objetos grandes, spill controlado e compactação periódica de arquivos pequenos. Lotes devem ter limites tanto por quantidade de objetos quanto por bytes.

**Critério de aceite:** o número de tabelas temporárias não cresce com o número de objetos; arquivos maiores que a memória são processados com streaming/spill; entradas são selecionadas por manifesto ou prefixo específico.

## 5. Ambiente local usado como topologia de disponibilidade

**O que está ruim:** Prefect e MinIO dependem de armazenamento local em instância única. Não há separação arquitetural formal entre desenvolvimento, homologação e produção.

**Por que precisa mudar:** falha do host ou do disco pode interromper a orquestração e tornar dados indisponíveis. O ambiente local não fornece redundância, failover nem recuperação comprovada.

**Substituir por:** manter Docker Compose apenas para desenvolvimento e criar uma topologia de produção com:

- banco PostgreSQL persistente e dedicado ao Prefect;
- MinIO distribuído ou serviço S3 compatível com redundância equivalente;
- PostgreSQL do Lakekeeper com backup e restore;
- workers separados por perfil de recurso;
- configurações independentes por ambiente;
- healthchecks de prontidão, não apenas de processo ativo.

**Critério de aceite:** desenvolvimento e produção possuem configurações isoladas; falha de um worker não interrompe toda a plataforma; serviços de estado podem ser restaurados dentro do RPO e RTO definidos.

## 6. Backup e recuperação não definidos

**O que está ruim:** volumes persistentes existem, mas não há política arquitetural de backup, restore, RPO, RTO ou teste de desastre.

**Por que precisa mudar:** persistência local não equivale a backup. Sem restauração testada, não é possível afirmar que catálogo, estados de orquestração e dados podem ser recuperados.

**Substituir por:** backups automatizados e versionados para PostgreSQL, catálogo e armazenamento; cópia em domínio de falha separado; runbook de recuperação; testes periódicos de restore e perda de nó/disco.

**Critério de aceite:** RPO e RTO estão aprovados; restaurações são executadas periodicamente; o tempo e a integridade da recuperação são registrados.

## 7. Credenciais administrativas compartilhadas e transporte sem TLS

**O que está ruim:** serviços compartilham credenciais administrativas do armazenamento e conexões são configuradas sem TLS.

**Por que precisa mudar:** o comprometimento de uma execução concede acesso amplo ao datalake e ao warehouse. Sem TLS, credenciais e dados podem trafegar sem criptografia fora do ambiente local.

**Substituir por:** identidades de menor privilégio por ambiente, camada e função; credenciais distintas para leitura e escrita; segredos gerenciados por Prefect Blocks/Secrets ou secret manager; TLS obrigatório fora do desenvolvimento local.

**Critério de aceite:** nenhuma carga usa credencial root; permissões são validadas por testes positivos e negativos; segredos não aparecem em código, logs ou arquivos versionados; conexões de produção exigem TLS.

## 8. Builds e inicialização não reproduzíveis

**O que está ruim:** imagens usam tags flutuantes e extensões DuckDB são instaladas durante a criação de conexões.

**Por que precisa mudar:** a mesma configuração pode produzir ambientes diferentes ao longo do tempo. A inicialização depende de rede externa e pode falhar mesmo quando os serviços internos estão saudáveis.

**Substituir por:** imagens fixadas por versão ou digest, dependências diretas declaradas no lock e extensões DuckDB instaladas durante o build da imagem. Em runtime, somente extensões já disponíveis devem ser carregadas.

**Critério de aceite:** builds repetidos usam os mesmos artefatos; a execução inicia sem baixar dependências; atualização de versão ocorre por mudança explícita e validada.

## 9. Observabilidade sem padrão de plataforma

**O que está ruim:** logs não seguem um contrato comum e não existem métricas padronizadas de volume, duração, recursos, qualidade e publicação.

**Por que precisa mudar:** não é possível comparar capacidade, detectar regressões ou relacionar uma versão publicada à execução que a produziu.

**Substituir por:** logs estruturados e métricas centralizadas com, no mínimo:

- `run_id`, versão do código, dataset e partição lógica;
- arquivos, bytes e registros lidos e escritos;
- registros válidos, rejeitados e duplicados;
- duração, throughput, retries e status;
- pico de memória, CPU e uso de spill;
- versão Bronze consumida e snapshot Iceberg publicado.

Adicionar dashboards e alertas para falhas, atraso, divergência de contagem, falta de espaço, crescimento de rejeições, excesso de arquivos pequenos e staging antigo.

**Critério de aceite:** uma execução pode ser rastreada da entrada ao snapshot; saturação e regressões geram alerta; capacidade e SLOs podem ser calculados a partir das métricas coletadas.

## 10. Ausência de manutenção do Iceberg e do armazenamento

**O que está ruim:** não existem políticas automatizadas para snapshots antigos, manifests, objetos órfãos, temporários abandonados e arquivos pequenos.

**Por que precisa mudar:** metadados e armazenamento crescem indefinidamente, aumentando custo e tempo de planejamento. Remoções manuais no warehouse podem quebrar a consistência do catálogo.

**Substituir por:** rotinas agendadas e auditáveis de expiração de snapshots, remoção segura de órfãos, compactação, limpeza de staging e aplicação de lifecycle no MinIO. O warehouse Iceberg deve ser alterado exclusivamente pelo catálogo.

**Critério de aceite:** retenção possui prazo definido; nenhum objeto do warehouse é removido fora do catálogo; crescimento de manifests e arquivos pequenos é monitorado e mantido dentro dos limites acordados.

## 11. Ordem de implementação

1. Publicação imutável, manifesto e idempotência.
2. Locks por partição e limites de recursos.
3. Leitura em lote, streaming e compactação.
4. Credenciais de menor privilégio, TLS e builds reproduzíveis.
5. Métricas, alertas e manutenção automatizada.
6. Topologia de produção, backup e recuperação testada.

Cada item deve ser executado em etapas que alterem no máximo cinco arquivos e somente será concluído quando seu critério de aceite possuir evidência reproduzível.
