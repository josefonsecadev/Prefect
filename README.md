# Pipeline de dados

## **Descrição**
O projeto tem o intuito de criar um workflow para gerenciamento de ETL por meio do Prefect para orquestrar as execuções, DuckDB para transformações e um datalake em MiniO

| Stack | Funções | Motivação |
|---|---|---|
| Prefect | Orquestrar execuções | Pouco consumo de memória <br> Definição clara de workers |
| DuckDB | Gerenciamento de dados | Uso de SQL <br> Velocidade de implementação |
| MiniO | Datalake | Versão Open Source do S3 |
| Iceberg | Metadados | Alteração de Schema sem mexer nos dados <br> ACID |

## **Arquitetura**

### **Flows**

A arquitetura dos flows do Prefect seguem o path

*pipelines/{nome do projeto}/{nome do flow}*

Dentro desta pasta é para conter os scripts seguindo padrão medalhão: **bronze**, **prata** e **ouro**. Individualmente com cada script dentro de seu arquivo e classe. Além do seguintes padrões:

* Todo script deve ter uma classe PipeCamada Ex: PipeBronze, PipePrata, PipeOuro
* Toda classe deve ter a função `execute` possuindo o decorador do `@flow` com o nome do e descrição do flow
* Todas as demais funções da classe devem começar com `_` sinalizando que é uma função interna utilizada pelo e possuir o decorador `@task`
* O flow que será executado deve ser criado no arquivo orquestrador.py com o decorador `@flow` executando todas as funções `execute` das classes
* O orquestrador também deve possuir a estrutura `if __name__ == main` para execução do flow geral
* As informações comuns e estáticas (Schema dos dados, nome da pipeline) devem estar dentro do info.py

**Exemplo**

*pipelines/camara_deputados/despesas/bronze.py*<br>
*pipelines/camara_deputados/despesas/prata.py*<br>
*pipelines/camara_deputados/despesas/info.py*<br>
*pipelines/camara_deputados/despesas/orquestrador.py*<br>



## **Execução Local**

A execução local é importante para debug dos flows. A única diferença da execução local para produção é o apontamento do serviço do datalake, por é necessário subir um serviço local do MiniO. Crie a versão local do .env para que as configurações locais estejam corretas

Configure o arquivo .env com as informações locais do MiniO

* Execute o docker compose do MiniO (Coloquei MiniO em local diferente por rodar em produção em outro servidor, lembrar de colocar nesse diretório e assim rodar tudo no mesmo compose e deixa o compose fora do git)
  * Docker Compose up --build -d
* Execute o docker compose do Prefect para subir o server
  * Docker Compose up --build -d
* Crie um launch.json com os configurações para execução
```
      {
        "version": "0.2.0",
        "configurations": [
          {
            "name": "Debug Prefect Flow",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/pipelines/PROJETO/FLOW/orquestrador.py",
            "console": "integratedTerminal",
            "env": {
              "PREFECT_API_URL": "http://localhost:${PREFECT_PORT}/api"
            }
          }
        ]
      }
```
* Execute no Debug do VS Code
