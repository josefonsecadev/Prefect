# TASK-0013 — Reduzir imagem Python do lakehouse

## Identificação
- Status: backlog
- Categoria: docker
- Tipo: melhoria
- Etiquetas: [docker, imagens, build]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: diagnóstico solicitado pelo usuário, TASK-0011.
- Criada em: 2026-11-04
- Atualizada em: 2026-11-04
- Dependências: TASK-0011; stack funcional para comparação.

## Objetivo e contexto
Dockerfile conserva build-essential e Poetry na imagem final, faz duas instalações Poetry e copia todo contexto permitido. Imagem antiga prefect-prefect-worker:latest tem 2,19GB (2,009GB exclusivos); imagem nova medida em 1,41GB; usar esse valor na comparação futura. Avaliar multi-stage e dependências de runtime mantendo Python 3.14.6/lock e funcionamento de Prefect/DuckDB.

## Escopo e referências
- Incluído: medir camadas da imagem nova, retirar ferramentas de build do runtime se dispensáveis e restringir contexto.
- Fora: alterar versões/regras de pipeline e remover dependências necessárias sem evidência.
- Arquivos: Dockerfile, .dockerignore, pyproject.toml/poetry.lock se indispensáveis.
- Risco: wheels/extensões nativas exigem bibliotecas compartilhadas.

## Critérios de aceite
- [ ] Tamanhos antes/depois e camadas documentados, sem meta percentual inventada.
- [ ] Bootstrap e serviços Prefect funcionam; flows completos reproduzidos pelo orquestrador conforme AGENTS.md.
- [ ] Nenhum segredo/contexto local incluído na imagem.

## Etapas
### E01 — Medir e reduzir runtime
- Status: backlog
- Estimativa: 4.500 tokens; até cinco arquivos (Dockerfile, .dockerignore, tarefa, índice e documentação).
- Ações: inspecionar history, implementar menor redução e construir imagem.
- Evidência: image inspect/history, tamanho e execução real; se exceder escopo dividir antes.
### E02 — Avaliar execução real
- Status: backlog
- Estimativa: 3.500 tokens; até três arquivos de controle/documentação.
- Ações: validar bootstrap, Prefect e flows completos sem criar testes artificiais.
- Evidência: estados terminais, ausência de bibliotecas faltantes e comparação de disco.

## Retomada
- Próxima ação: medir imagem prefect-lakehouse-worker:local construída pela TASK-0011.
- Implementação futura, não executada.

## Histórico
| Data | Evento | Evidência |
|---|---|---|
| 2026-11-04 | Registrada otimização | Compiladores/Poetry permanecem no runtime |
