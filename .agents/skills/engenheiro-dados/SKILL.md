---
name: engenheiro-dados
description: Implementar, alterar, diagnosticar e revisar flows Prefect de pipelines de dados neste projeto. Usar quando a demanda envolver coleta de APIs com Requests, extração de páginas dinâmicas com Selenium, persistência Bronze no MinIO, transformação com DuckDB, publicação de tabelas Apache Iceberg pelo catálogo REST Lakekeeper, camadas Prata/Ouro, deployments, reprocessamento, idempotência ou observabilidade operacional.
---

# Engenheiro de Dados

Construir flows Prefect aderentes à arquitetura medalhão do projeto, com contratos explícitos, execução idempotente e falhas observáveis.

## Preparar o trabalho

1. Ler `AGENTS.md`.
2. Inspecionar o pipeline, as abstrações de `utils/`, o `prefect.yaml` e as dependências relacionadas.
3. Confirmar que a arquitetura necessária já foi definida. Encaminhar decisões transversais ainda abertas para `$arquiteto-software` e decisões de modelagem ou persistência para a skill de Arquiteto de Banco de Dados.
4. Definir o resultado observável, a fonte, o volume, a frequência, o recorte de reprocessamento, o consumidor e as camadas afetadas.
5. Planejar etapas com no máximo cinco arquivos, sem criar barreiras de teste entre etapas ou skills.

Não iniciar implementação enquanto estiverem indefinidos contratos que alterem particionamento, idempotência, schema, disponibilidade ou segurança.

## Execução local

1. Ler integralmente o flow solicitado antes de executá-lo. Procurar erros concretos, sem ampliar a análise para melhorias, `utils` ou funções genéricas.
2. Conferir se existe uma configuração do flow em `.vscode/launch.json`, com o módulo `pipelines.<mini_projeto>.<flow>.orquestrador`, a `.venv` do projeto e o `.env`.
3. Executar `docker compose ps` e somente prosseguir quando Prefect Server, MinIO, Lakekeeper e banco do catálogo estiverem ativos e saudáveis.
4. Distinguir os endpoints conforme o processo que executará o flow:
   - dentro do Docker, usar os nomes dos serviços, como `minio`, `lakekeeper` e `prefect-server`;
   - no host Windows, sobrescrever na configuração de debug:

     ```json
     {
       "MINIO_ENDPOINT": "localhost:9000",
       "ICEBERG_CATALOG_ENDPOINT": "http://localhost:8181/catalog",
       "PREFECT_API_URL": "http://127.0.0.1:4200/api"
     }
     ```

5. Iniciar pelo perfil de debug do VS Code. Não executar `debugpy/launcher` isoladamente: ele exige que o adaptador do VS Code já esteja escutando e, sem isso, falha com `WinError 10061`.
6. Quando o harness não puder controlar uma sessão do VS Code, executar o mesmo entrypoint com o interpretador explícito do projeto e as mesmas variáveis do perfil:

   ```powershell
   & '.venv\Scripts\python.exe' -m pipelines.<mini_projeto>.<flow>.orquestrador
   ```

7. Se a execução ultrapassar o timeout do terminal, verificar processos Python e os runs no Prefect antes de iniciar outra. Nunca presumir que o timeout encerrou o processo; evitar dois runs concorrentes do mesmo recorte.
8. Consultar estados sem truncamento pelo módulo da própria `.venv`, evitando um `prefect.exe` que possa apontar para outro ambiente:

   ```powershell
   $env:PREFECT_API_URL='http://127.0.0.1:4200/api'
   & '.venv\Scripts\python.exe' -m prefect flow-run ls --limit 10 -o json
   ```

9. Interpretar falhas de ambiente antes de propor mudança no flow:
   - servidor temporário e `No module named uvicorn`: `PREFECT_API_URL` não foi aplicado;
   - falha ao resolver `lakekeeper`: endpoint interno do Docker usado por uma execução no host;
   - `WinError 10013` em API externa ou erro ao gravar em `~/.prefect`: restrição do sandbox, devendo solicitar execução fora dele;
   - erro de serialização do cache envolvendo a instância da pipeline: registrar separadamente se a task continuar e identificar a exceção que efetivamente definiu o estado final.
10. Acompanhar Bronze, Prata/Ouro e orquestrador até um estado terminal. Em caso de erro real do flow ou da configuração versionada, aplicar a menor correção dentro do escopo e executar novamente. Repetir até o flow terminar sem falhas.

## Escolher a extração

- Preferir Requests quando a fonte expuser API ou conteúdo acessível sem execução de JavaScript.
- Usar Selenium somente quando a interação com navegador for indispensável e essa necessidade tiver sido comprovada.
- Ler [extracao.md](references/extracao.md) antes de implementar coleta, paginação, autenticação, download ou scraping.
- Persistir na Bronze a resposta original, ou a representação mais fiel possível, antes de aplicar regras de negócio.

## Implementar o flow

Seguir a organização existente:

```text
pipelines/<mini_projeto>/<flow>/
├── orquestrador.py
├── bronze.py
├── prata.py
├── ouro.py       # somente quando houver consumidor definido
└── info.py
```

1. Centralizar nomes, schemas e metadados específicos em `info.py`.
2. Resolver parâmetros de execução uma única vez no orquestrador e repassar valores tipados às camadas.
3. Usar `@flow` para composição e `@task` apenas em unidades que precisem de retry, timeout, cache, concorrência ou estado operacional próprio.
4. Manter funções puras como funções comuns e capacidades compartilhadas por dois ou mais pipelines em `utils/`.
5. Fazer exceções alcançarem o estado do flow. Não registrar erro e continuar como sucesso.
6. Aplicar retry somente a falhas transitórias, sempre com limite e atraso definidos. Falhar imediatamente em erro de contrato, schema ou regra de negócio.
7. Nunca registrar tokens, cookies, credenciais, payloads sensíveis ou URLs assinadas.

## Transformar e publicar

- Usar DuckDB para leitura, tipagem, validação, joins e agregações; evitar materialização em Python quando SQL resolver o processamento de forma mais eficiente.
- Publicar Prata e Ouro como tabelas Iceberg transacionais por meio do catálogo REST Lakekeeper.
- Manter PostgreSQL apenas como persistência interna do Lakekeeper.
- Ler [publicacao.md](references/publicacao.md) antes de alterar SQL, schema, particionamento, catálogo, snapshots ou escrita Iceberg.
- Garantir que repetir o mesmo recorte não duplique registros nem substitua partições fora do escopo.

## Validar o flow localmente

1. Não criar nem alterar arquivos de testes, fixtures ou mocks, salvo solicitação explícita do usuário.
2. Não executar testes unitários, testes isolados, scripts temporários, compilação isolada ou simulações antes de passar para outra etapa ou skill.
3. Concluir a implementação planejada e então executar localmente o orquestrador do flow completo com os serviços obrigatórios ativos.
4. Acompanhar a execução real de Bronze, Prata/Ouro e orquestrador. Usar os logs, estados do Prefect e artefatos publicados para localizar erros.
5. Corrigir somente a causa concreta encontrada e reproduzir o flow novamente. Repetir o ciclo até uma execução completa sem falhas.
6. Considerar a execução local bem-sucedida como o teste do flow. Em Iceberg, confirmar na própria execução o schema, a quantidade de registros e o snapshot publicado quando essas evidências estiverem disponíveis.
7. Se infraestrutura, credenciais ou serviços indisponíveis impedirem a reprodução, registrar o bloqueio e não substituir o flow por testes artificiais.

Entregar o comportamento implementado, arquivos alterados, comando e resultado da execução local e qualquer decisão que precise voltar ao planejamento.
