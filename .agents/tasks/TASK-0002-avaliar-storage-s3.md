# TASK-0002 — Decidir substituto do MinIO

## Identificação

- Status: bloqueada
- Categoria: infraestrutura
- Tipo: investigacao
- Etiquetas: [s3, minio, rustfs, garage, seaweedfs, docker, iceberg, lakekeeper]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário quer decidir junto entre RustFS, Garage e SeaweedFS para substituir MinIO.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: nenhuma tarefa; escolha depende dos requisitos abaixo.

## Objetivo e contexto

Escolher armazenamento S3 de código aberto que preserve Bronze e o warehouse
Iceberg usado por DuckDB e Lakekeeper. Nesta tarefa, entregar comparação e decisão;
a migração será detalhada em tarefa posterior após a escolha.

Fatos confirmados na inspeção:

- Compose usa `minio/minio:latest`, volume `D:/Dados`, bootstrap com `minio/mc`.
- `utils/conexoes.py` usa SDK Python MinIO e configura DuckDB com endpoint S3,
  região `us-east-1`, path-style e credenciais estáticas.
- O bootstrap Lakekeeper registra endpoint MinIO, `flavor=minio` e STS desabilitado.
  Um HTTP 409 é aceito sem atualizar o perfil do warehouse já existente.
- Logo, trocar só a imagem não resolve configuração, bootstrap e catálogo existente.
- Não há `graphify-out/graph.json` no checkout consultado.

## Escopo e contratos

- Incluído: pesquisa oficial, comparação, requisitos e decisão conjunta.
- Fora do escopo: trocar containers, mover dados, alterar credenciais ou o catálogo.
- Preservar: nomes lógicos e conteúdo das tabelas, snapshots e Bronze; nenhuma exclusão autorizada.
- Referências locais: `docker-compose.yml`, `utils/conexoes.py`, `.agents/knowledge/planning.md`.
- Em aberto: ambiente local ou produção; volume atual e crescimento; uma máquina ou
  cluster; disponibilidade necessária; dados/snapshots a preservar; importância da interface web.

## Comparação preliminar em 2026-11-03

| Opção | Evidência oficial | Avaliação para este projeto |
|---|---|---|
| RustFS | Apache-2.0; 1.0 GA anunciada em 16/09/2026; releases 1.0.x | Candidato para manter foco em S3, mas histórico estável recente pede validação operacional |
| Garage | AGPLv3; foco em operação leve e distribuição geográfica; matriz S3 declara limitações | Candidato quando baixo consumo e replicação distribuída forem prioritários; verificar APIs necessárias |
| SeaweedFS | Apache-2.0; arquitetura master, volume, filer e acesso S3 | Candidato preferencial preliminar para priorizar histórico operacional, aceitando mais conceitos de operação |

A preferência é julgamento arquitetural, não benchmark nem compatibilidade validada.
Nenhuma opção foi escolhida. Ausência de bucket versioning no Garage não equivale
à ausência de snapshots Iceberg; são mecanismos diferentes. Compatibilidade deve
ser confirmada na versão exata, com o Lakekeeper 0.12.1 usado no projeto.

Fontes consultadas:

- [MinIO: AGPLv3 e arquivo em 25/04/2026](https://github.com/minio/minio)
- [RustFS: GA em setembro de 2026](https://www.rustfs.com/blog/announcing-rustfs-1-0-0-ga/)
- [RustFS: releases](https://github.com/rustfs/rustfs/releases)
- [Garage: licença e objetivo](https://github.com/deuxfleurs-org/garage)
- [Garage: compatibilidade S3](https://garagehq.deuxfleurs.fr/documentation/reference-manual/s3-compatibility/)
- [Garage: consistência configurável](https://garagehq.deuxfleurs.fr/documentation/reference-manual/configuration/)
- [SeaweedFS: código, licença e arquitetura](https://github.com/seaweedfs/seaweedfs)
- [SeaweedFS: operação em produção](https://github.com/seaweedfs/seaweedfs/wiki/Production-Setup)

O código comunitário MinIO continua AGPLv3 no repositório arquivado. A justificativa
confirmada para avaliar saída é continuidade de manutenção/distribuição; não foi
confirmado que esse código tenha deixado de ser open source.

## Critérios de aceite

- [x] Comparação baseada em fontes oficiais e integração atual inspecionada.
- [ ] Requisitos de ambiente, disponibilidade e preservação esclarecidos.
- [ ] Usuário escolheu a alternativa e os motivos foram registrados.
- [ ] Próxima tarefa de migração definida em etapas de até 5.000 tokens e cinco arquivos.

## Etapas

### E01 — Comparação inicial

- Status: concluida
- Estimativa: 4.500 tokens, incluindo pesquisa, inspeção e registro.
- Premissas: consulta documental; sem benchmark ou execução de serviços.
- Arquivos: este registro e `.agents/tasks/README.md`.
- Entrega: comparação preliminar e identificação dos pontos de integração.
- Validação: fontes oficiais conferidas, código/configuração lidos e revisão documental.
- Evidência: URLs e fatos locais registrados acima; nenhuma compatibilidade executável alegada.
- Branch: `codex/avaliar-storage-s3`.

### E02 — Fechar escolha e delimitar migração

- Status: bloqueada
- Estimativa: 3.000 tokens.
- Premissas: usuário informa requisitos operacionais e decide entre as alternativas.
- Dependências: E01 e respostas do usuário.
- Arquivos previstos: este registro, índice e eventual tarefa de migração (três arquivos).
- Entrega: decisão com critérios e tarefa posterior delimitada, sem migrar durante a discussão.
- Validação: escolha explícita registrada; etapas futuras dentro dos limites.
- Resultado e evidências: pendente.

## Retomada

- Próxima etapa: E02.
- Feito: pesquisa e comparação preliminar; armazenamento atual preservado.
- Próxima ação: confirmar se o alvo é ambiente local ou produção e quais dados precisam ser preservados.
- Bloqueio: decisão arquitetural conjunta pendente; retomar com requisitos e escolha do usuário.
- Validação pendente: decisão; reprodução de flows será aceite da futura migração.

## Histórico

| Data | Evento | Evidência/motivo |
|---|---|---|
| 2026-11-03 | Registrada investigação; E01 concluída, E02 aguardando usuário | Pedido explícito de decidir juntos; fontes e integração inspecionadas |
