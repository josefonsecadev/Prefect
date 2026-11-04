# TASK-0014 — Definir retenção de imagens e cache Docker

## Identificação
- Status: backlog
- Categoria: docker
- Tipo: manutencao
- Etiquetas: [docker, disco, cache]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: diagnóstico solicitado pelo usuário, TASK-0011.
- Criada em: 2026-11-04
- Atualizada em: 2026-11-04
- Dependências: TASK-0011.

## Objetivo e contexto
Inventário antes da subida: imagens 4,276GB; cache 3,994GB, dos quais 1,892GB recuperáveis; volumes 85,53MB. Existem imagens antigas MinIO, mc, Lakekeeper e Prefect sem containers. Isso não autoriza exclusão: verificar uso por outros projetos e rollback. VHDX lógico de 12.373.196.800 bytes durante pull; tamanho do arquivo não equivale necessariamente a alocação física ou tamanho das imagens.

## Escopo e referências
- Incluído: inventário por projeto, retenção por idade/uso, limpeza seletiva revisável e política de cache; avaliar compactação apenas após backup e medição física.
- Fora: prune amplo, exclusão de volumes, limpeza automática indiscriminada ou promessa de recuperar soma dos tamanhos virtuais.
- Referências: Docker system df -v, buildx du, .dockerignore, documentação de operação.
- Preservar todos os dados e credenciais; imagens podem compartilhar camadas com cache.

## Critérios de aceite
- [ ] Lista exata de candidatos, dependências e impacto revisada antes de remover.
- [ ] Medições antes/depois distinguem imagens, cache, volumes e VHDX físico/lógico.
- [ ] Stack e outros projetos preservados; procedimento de retenção documentado.

## Etapas
### E01 — Inventário e política
- Status: backlog
- Estimativa: 2.500 tokens; três arquivos (tarefa, índice e documentação).
- Ações: classificar candidatos e propor comandos seletivos sem execução destrutiva.
- Evidência: tamanhos exclusivos/compartilhados, uso e idade.
### E02 — Limpeza autorizada e avaliação
- Status: backlog
- Estimativa: 2.500 tokens; três arquivos de controle/documentação.
- Ações: aplicar lista autorizada, medir economia e verificar stack. Compactação é etapa separada se necessária.
- Evidência: diff do inventário e saúde pós-limpeza.

## Retomada
- Próxima ação: coletar inventário final após build e classificar candidatos com o usuário.
- Nenhuma limpeza executada nesta demanda.

## Histórico
| Data | Evento | Evidência |
|---|---|---|
| 2026-11-04 | Registrada manutenção futura | Cache antigo e imagens fora do Compose atual |
