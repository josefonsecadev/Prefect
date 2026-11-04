# TASK-0011 — Diagnosticar stack Docker e recursos

## Identificação
- Status: concluida
- Categoria: observabilidade
- Tipo: investigacao
- Etiquetas: [docker, memoria, disco]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário pediu confirmar recuperação do Docker, subir projeto, medir RAM/disco e registrar otimizações futuras.
- Criada em: 2026-11-04
- Atualizada em: 2026-11-04
- Dependências: Docker Engine acessível

## Objetivo e contexto
Confirmar prontidão da stack e registrar consumo real sem confundir repouso com pico de flows. Hipervisor ativo e Engine 29.6.1 respondendo após habilitação da virtualização.

## Escopo e referências
- Incluído: Compose existente, healthchecks, bootstraps, amostras RAM, inventário de imagens/cache/volumes e backlog de otimização.
- Fora: executar otimizações, apagar imagens/volumes, validar flows e conceder aceite às TASK-0005 a 0010.
- Referências: docker-compose.yml, Dockerfile, README.md, TASK-0010.
- Preservar arquitetura, credenciais e persistência; Prefect opera em janela.

## Critérios de aceite
- [x] Subida tentada e prontidão/falhas documentadas.
- [x] RAM e disco medidos com limitações explícitas.
- [x] Oportunidades registradas sem duplicar TASK-0010.

## Etapas
### E01 — Diagnóstico e backlog
- Status: concluida
- Estimativa: 4.500 tokens; medições operacionais e documentação, sem alteração de código.
- Arquivos previstos: esta tarefa, README do backlog e até três tasks futuras (máximo cinco).
- Ações: subir stack padrão e processing para diagnóstico, verificar prontidão, medir recursos, registrar evidências e desligar processing ocioso.
- Validação: Docker Compose, inspect, stats e system df.
- Branch: codex/diagnostico-docker-recursos
- Resultado: diagnóstico concluído; stack não aceita, impedimento operacional registrado abaixo.

## Retomada
- Próxima ação: planejar TASK-0012 e repetir subida/prontidão após estabilizar WSL.
- Bloqueio operacional: Docker/WSL perdeu responsividade durante startup; não foi possível medir stack completa.

## Histórico
| Data | Evento | Evidência |
|---|---|---|
| 2026-11-04 | Diagnóstico iniciado | Hipervisor ativo; Docker Engine 29.6.1 |


## Diagnóstico — 2026-11-04, aproximadamente 18:14 (America/Sao_Paulo)

### Recuperação e execução
- HypervisorPresent=True; Engine Linux 29.6.1 / Desktop 4.80.0 respondeu inicialmente.
- Grafo graphify-out/graph.json ausente neste checkout; consulta substituída por leitura de Compose, Dockerfile e documentação. Nenhum código foi alterado; não houve atualização do grafo.
- Executado docker compose up --build -d: pull das quatro imagens novas e build de prefect-lakehouse-worker:local bem-sucedidos.
- PostgreSQL e RustFS passaram nos healthchecks. polaris-bootstrap encerrou com código 0. Polaris iniciou, porém última leitura disponível ainda mostrava health: starting. Cache interno Polaris reportado em aproximadamente 64MB.
- lakehouse-setup e Trino permaneceram Created na última leitura. Prefect não foi iniciado: pertence ao profile processing, e as dependências da base não concluíram.
- Compose encerrou com código 1: inspect do Polaris recebeu HTTP 500 na API v1.54. A mensagem de compatibilidade da API é genérica e não comprova incompatibilidade de versão.
- wsl -d docker-desktop para ler meminfo/pressure/swaps falhou com Wsl/Service/0x8007274c (timeout). Log posterior do backend registra stats GET /ping com context deadline exceeded.
- Não declarar todos os serviços up. Nenhum reset, prune, remoção de imagens/volumes ou alteração de memória foi feito. Containers/volumes preservados; estado final exato indisponível após perda de resposta. Não houve flows ativos iniciados por esta avaliação.

### RAM (amostras, não picos sincronizados)
| Escopo | Medição |
|---|---|
| Host físico | 16.421.335.040 bytes, 15,29GiB |
| WSL configurado | 1GiB / quatro CPUs |
| MemTotal reportado pelo Engine | 940.691.456 bytes, 897,1MiB |
| Base: soma de limites | 1.168MiB; não é reserva nem consumo |
| Polaris em startup | 175,1MiB / limite 320MiB |
| PostgreSQL na mesma amostra | 10,19MiB / limite 80MiB |
| RustFS na mesma amostra | 28,09MiB / limite 192MiB |
| Soma desses três containers | 213,38MiB; Trino e Prefect ausentes |
| Bootstrap Java, amostra anterior | 122MiB; processo já encerrado |
| Windows: vmmemWSL final | 1.010,6MiB de working set |
| Windows: backends Docker agregados | 218,6MiB de working set |
| Windows: processos Docker Desktop agregados | 539,7MiB de working set |
| Host livre na amostra final | 4.501.692KiB, aproximadamente 4,29GiB |

Working sets Windows podem compartilhar páginas; não somar como RAM exclusiva. Docker stats em Linux desconta cache; não equivale à memória da VM. Não há medição cgroup/PSI/swap concluída. Último inspect antes da falha: OOMKilled=false e RestartCount=0 em seis containers (alguns ainda Created). Isso não exclui pressão global nem comprova causa. Capacidade de 1GiB é hipótese prioritária, com instabilidade comprovada; meta de 2GB continua sem aceite e carga real permanece na TASK-0010/E02.

### Disco após pull/build, antes da falha
| Categoria Docker system df | Total | Recuperável informado |
|---|---:|---:|
| Imagens (13) | 8,585GB | 2,439GB |
| Cache de build (23 registros) | 3,996GB | 1,893GB |
| Volumes (6) | 134,2MB | 85,53MB |
| Camadas graváveis containers | 135,2kB | 28,67kB |

| Imagem atual do Compose | Tamanho virtual reportado |
|---|---:|
| trinodb/trino:484 | 2,41GB |
| prefect-lakehouse-worker:local | 1,41GB |
| apache/polaris:1.8.0 | 1,18GB |
| apache/polaris-admin-tool:1.8.0 | 854MB |
| rustfs/rustfs:1.0.4 | 419MB |
| postgres:16.9-alpine | 395MB |

Imagens antigas presentes: worker 2,19GB, prefecthq/prefect 1,22GB, Lakekeeper 225MB, MinIO 241MB, mc 117MB, curl 41,7MB e base Python 180MB. Algumas camadas são compartilhadas; tamanho virtual e recuperável não são valores somáveis entre categorias. Imagens usadas não podem ser tratadas como lixo.

VHDX de dados: Length final 14.889.779.200 bytes (13,87GiB); arquivo principal ext4 observado antes com 100.663.296 bytes. Length é tamanho lógico, não medição da alocação física NTFS. Antes dos pulls, C: possuía aproximadamente 280,39GiB livres e D: 116,10GiB livres. Não há indicação de falta de espaço por esses dados.

### Otimizações futuras
1. TASK-0012 (P1): orçamento da VM/containers e diagnóstico de pressão, integrado ao pico real da TASK-0010.
2. TASK-0013 (P2): medir camadas e retirar compiladores/Poetry do runtime quando seguro; imagem nova de referência 1,41GB. O cache foi aproveitado e o contexto do build atual tinha 601,48kB, portanto contexto grande não está demonstrado nesta execução.
3. TASK-0014 (P2): retenção seletiva de imagens/cache; não executar prune amplo nem apagar volumes. Medir economia real e eventual VHDX físico antes de considerar compactação.

### Avaliação
Aprovada documentação de diagnóstico e backlog; reprovado aceite operacional da stack. Critérios desta investigação atendidos por tentativa real, medições parciais e impedimento explícito. TASK-0005/0006/0008/0009/0010 não foram concluídas por esta demanda. Nenhum teste artificial criado. Diff revisado para cinco arquivos de controle, sem segredos. Commit local somente; push não solicitado.

Referências de interpretação: https://docs.docker.com/reference/cli/docker/system/df/ e https://docs.docker.com/reference/cli/docker/container/stats/ .
