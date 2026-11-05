---
name: engenheiro-dados
description: Implementar, diagnosticar e executar flows Prefect de coleta, transformação e publicação em RustFS/Parquet ou Iceberg/Nessie neste projeto.
---

# Engenharia de Dados

## Preparação direcionada
- Reutilize AGENTS.md, task e contexto já lido. Inspecione orquestrador, camadas e
  helpers usados, ampliando leitura apenas para entender contratos/efeitos da mudança.
- Confirme fonte, camadas, recorte, formatos e critério de aceite. Não criar nova
  camada/regra/modo porque apareceu uma falha; decisão essencial volta ao planejamento.
- Etapas até cinco arquivos e 5.000 tokens estimados; uma branch por demanda.
  Só arquivos relacionados, sem testes artificiais como barreira entre etapas.
- Leia `references/extracao.md` para mudança de extração e `references/publicacao.md`
  para publicação/schema/particionamento, somente quando pertinentes e ainda não lidos.

## Execução local e diagnóstico
1. Conferir `docker compose ps` uma vez e observar serviços necessários ao modo
   escolhido. Parquet direto requer RustFS/Prefect; Iceberg requer Nessie.
   ClickHouse só quando fizer parte do aceite. Não iniciar dependências fora do escopo.
2. Usar perfil `.vscode/launch.json`, `.venv` e `.env` do checkout. No host usar
   localhost; no container usar DNS dos serviços. Sem controle do VS Code, executar
   o mesmo entrypoint com `.venv/Scripts/python.exe -m pipelines.<projeto>.<flow>.orquestrador`
   e as variáveis do perfil. Launcher debugpy isolado exige adaptador e não funciona.
3. Um flow por vez. Timeout do terminal não encerra necessariamente o processo:
   conferir processo/run antes de nova execução. Para estados usar a própria `.venv`
   com `-m prefect flow-run ls --limit 10 -o json`, reduzindo saída aos runs pertinentes.
4. Guardar logs completos em arquivo ignorado; retornar estado, run ID e trecho causal.
   Acompanhar em intervalos de 20–30s ou eventos, sem polling curto repetitivo.
   Não refazer build/checks sem alteração ou nova evidência que justifique.
5. Diferenciar ambiente, fonte externa, contrato e código. Cache envolvendo `self`/
   conexão DuckDB pode falhar sem ser a causa terminal; localizar erro real.
6. Corrigir menor causa dentro do escopo e repetir orquestrador completo. Fonte externa
   esgotou retries e mantém falha: registrar impedimento, parar chamadas idênticas e
   continuar trabalho independente. Retomar após correção/condição nova, sem dados falsos.

## Implementação e persistência
- Organização: `orquestrador.py` compõe camadas, `info.py` guarda metadados/schema;
  helpers específicos permanecem no pipeline e compartilhados em utils quando comuns.
- Resolver parâmetros uma vez, repassar valores tipados; tasks para unidades que
  precisam de observabilidade/retry/estado próprio. Não silenciar exceções.
- Requests para APIs; Selenium somente quando navegador for indispensável. Timeout,
  paginação limitada, schema mínimo, preservação Bronze e retries só transitórios.
- DuckDB para transformação, projeção/filtro cedo e memória/temporários controlados;
  evitar materializar em Python quando SQL resolve. Segredos nunca em logs/Git.
- Respeitar formato escolhido no contrato: Iceberg com commit REST Nessie e snapshots;
  Parquet direto conforme exceção aprovada no planning/task, sem alegar transações
  ou validar catálogo. Nessie mantém exclusivamente metadados do catálogo.
- Escrita idempotente por recorte, sem duplicar ou apagar partições alheias. Validar
  tipos/identificadores SQL e reconciliar contagens/valores conforme regra aprovada.

## Aceite e retomada
- Depois da implementação, reproduzir flow completo pelo ambiente/perfil do projeto
  até estado terminal sem falhas. Conferir artefatos/schema/contagens e snapshots
  quando aplicáveis. Healthcheck não valida resultado de negócio.
- Sem testes unitários/integração, fixtures, mocks, scripts temporários ou simulações
  como substituto; criá-los somente por solicitação explícita. Estresse induzido não
  substitui execução funcional bem-sucedida.
- Bloqueio externo/decisão de negócio pendente mantém aceite pendente. Registrar
  causa, comando/recorte/run ID, evidência resumida e próximo passo na task.
- Entrega curta: mudança, validação real e limitações. Não repetir logs/planejamento.
