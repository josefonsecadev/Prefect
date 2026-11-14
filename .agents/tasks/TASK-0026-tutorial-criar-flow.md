# TASK-0026 — Documentar criação de um flow novo

- Status: concluida
- Categoria: documentacao
- Tipo: melhoria
- Prioridade: P2
- Origem: pedido explícito do usuário, 2026-11-05.

## Objetivo e escopo
Adicionar ao README um tutorial pequeno e compatível com a estrutura atual do
projeto para criar um flow por pipeline, declarar schemas, compor camadas, registrar
deployment no Prefect e executá-lo localmente ou pelo Worker.

## Critérios de aceite
- [x] O tutorial aponta os arquivos corretos e explica que `info.py` guarda metadados/schema.
- [x] O tutorial mostra como registrar o entrypoint em `prefect.yaml` e executar/reconstruir o Worker.
- [x] `git diff --check` sem erros.

## Etapas

### E01 — Tutorial curto no README

- Status: concluida
- Estimativa: até 1.000 tokens
- Arquivos previstos: README.md, este registro e `.agents/tasks/README.md`.
- Resultado e evidências obtidas: seção "Criar um flow novo" adicionada ao README; revisão documental e `git diff --check` aprovados.

## Retomada

- Etapa atual/próxima: nenhuma.
- Bloqueio: nenhum.

## Histórico

| Data | Evento | Evidência/motivo |
|---|---|---|
| 2026-11-05 | Tarefa registrada | Pedido do usuário para documentar a criação de flows no README. |
