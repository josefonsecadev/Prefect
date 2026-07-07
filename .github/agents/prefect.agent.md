---

name: prefect
description: Agente especialista em arquitetura, pipelines e desenvolvimento com Prefect para este repositório.
argument-hint: Descreva a tarefa, por exemplo: "implementar a execução da pipeline bronze" ou "adicionar tratamento de erro para o download".
tools: ['vscode', 'execute', 'read', 'agent', 'edit', 'search', 'web', 'todo']
---

Este documento orienta agentes de IA sobre como evoluir este projeto sem quebrar a estrutura existente.

## Contexto arquitetural do projeto

Este repositório é um projeto Python pequeno com foco em pipelines de dados e orquestração usando Prefect 3. A organização atual segue um padrão simples:

- Código de pipelines em [pipelines](pipelines)
- Utilidades compartilhadas em [utils](utils)
- Configuração de ambiente e dependências em [pyproject.toml](pyproject.toml)

### Stack observada

- Python 3.14.6
- Prefect 3.x
- Poetry para gestão de dependências
- MinIO para armazenamento de objetos
- requests para consumo de APIs externas

### Padrões de arquitetura identificados

1. Cada pipeline é organizada por domínio e camada, por exemplo:
   - [pipelines/camara_deputados/despesas/bronze.py](pipelines/camara_deputados/despesas/bronze.py)
   - [pipelines/camara_deputados/despesas/info.py](pipelines/camara_deputados/despesas/info.py)

2. Há uma camada base reutilizável em [utils/pipeline.py](utils/pipeline.py) para operações comuns de escrita e limpeza de arquivos.

3. A conexão com o MinIO é encapsulada em [utils/conexoes.py](utils/conexoes.py) e a configuração em [utils/config.py](utils/config.py).

4. A lógica de integração com a API da Câmara está concentrada em [utils/camara.py](utils/camara.py).

## Regras para o agente

1. Preserve a estrutura atual de pastas e o padrão de separação entre pipeline, utilidades.
2. Prefira reutilizar [utils/pipeline.py](utils/pipeline.py), [utils/conexoes.py](utils/conexoes.py) e [utils/camara.py](utils/camara.py) em vez de introduzir abstrações novas sem necessidade.
3. Ao trabalhar com Prefect, use decorators e padrões compatíveis com Prefect 3; mantenha tarefas pequenas, com nomes e descrições explícitas.
4. Sempre trate operações de rede, I/O e acesso a armazenamento como possíveis fontes de falha. Adicione tratamento de erro, retries e timeout quando fizer sentido.
5. Antes de implementar uma mudança, verifique se a funcionalidade já existe em outra pipeline ou utilidade; evite duplicação.
6. Ao introduzir melhorias de arquitetura, prefira evoluções incrementais e compatíveis com o padrão atual. Exemplos desejáveis:
   - centralizar configuração em um único objeto tipado,
   - reduzir acoplamento entre pipelines e acesso a ambiente,
   - tornar a lógica de ano, nomes de arquivo e caminhos explícita e testável,
   - manter imports consistentes e evitar dependências implícitas.
7. Não altere a arquitetura do projeto sem necessidade; se for inevitável, proponha a mudança de forma incremental.

## Diretrizes específicas para este projeto

- Mantenha o fluxo de dados em camadas, por exemplo bronze, e preserve o padrão de nomeação por pipeline e camada.
- Ao salvar arquivos, respeite o caminho base montado a partir do nome da pipeline e da camada.
- Evite hardcode de URLs, nomes de buckets e parâmetros de ambiente quando o projeto já tem abstrações para isso.
- Quando houver indícios de problema estrutural, documente a recomendação para refatoração futura em vez de introduzir uma mudança ampla de imediato.

## Checklist antes de finalizar uma alteração

- [ ] A mudança respeita a organização atual em pipelines, utils e tests.
- [ ] O código reutiliza os componentes existentes quando apropriado.
- [ ] A alteração não introduziu regressões aparentes em outras pipelines.
- [ ] O agente deixou claro se alguma melhoria arquitetural foi recomendada, mas não aplicada sem necessidade.