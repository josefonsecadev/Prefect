# Extração com Requests e Selenium

## Contrato comum

Definir antes do código:

- endpoint ou página de origem e método de autenticação;
- parâmetros, paginação, janela temporal e condição de término;
- formato, encoding, compressão e schema mínimo esperado;
- timeout de conexão e leitura, política de retry e limites de taxa;
- chave do objeto Bronze e metadados de rastreabilidade;
- comportamento para resposta vazia, parcial, duplicada ou fora do contrato.

## Requests

1. Reutilizar uma `requests.Session` quando houver múltiplas chamadas à mesma origem.
2. Informar timeout explícito; quando útil, separar conexão e leitura com uma tupla.
3. Validar status HTTP antes de interpretar o corpo. Tratar `429` e falhas `5xx` como potencialmente transitórias; não repetir automaticamente erros determinísticos `4xx`.
4. Validar `Content-Type`, tamanho, estrutura mínima e campos obrigatórios antes de persistir.
5. Implementar paginação com condição de parada observável e proteção contra páginas repetidas ou loop infinito.
6. Preservar bytes ou JSON originais na Bronze. Registrar endpoint lógico, recorte, página, quantidade, checksum e horário, nunca segredos.
7. Fazer download em streaming para conteúdos grandes, evitando carregar o arquivo inteiro sem necessidade.

Não esconder falha com retorno vazio. Diferenciar ausência legítima de dados de erro de origem ou quebra de contrato.

## Selenium

Usar somente após confirmar que Requests não atende porque a página depende de JavaScript, interação, sessão de navegador ou desafio compatível com automação autorizada.

1. Confirmar permissão de acesso e respeitar limites, termos e dados pessoais da fonte.
2. Executar navegador headless no ambiente automatizado, com versão do driver compatível e dependências reproduzíveis na imagem Docker.
3. Criar e encerrar o driver dentro de `try/finally` ou gerenciador de contexto.
4. Preferir `WebDriverWait` e condições explícitas; não depender de `sleep` fixo para sincronização.
5. Usar seletores estáveis baseados em semântica, atributos ou estrutura controlada. Evitar classes geradas e posições absolutas frágeis.
6. Limitar páginas, cliques, downloads e tempo total. Detectar repetição e mudanças inesperadas de navegação.
7. Persistir HTML, arquivo baixado ou representação original relevante na Bronze antes da normalização.
8. Em falha, registrar URL lógica, etapa e seletor sem incluir cookies, tokens ou conteúdo sensível. Captura de tela deve ser diagnóstica, sanitizada e ter retenção definida.

Não tentar contornar CAPTCHA, controles de acesso ou bloqueios anti-automação. Encaminhar esse impedimento ao planejamento.

## Observabilidade na execução local

- Registrar recorte, página, tentativas, duração, bytes e registros coletados.
- Não criar fixtures, mocks ou arquivos de testes para validar a extração, salvo solicitação explícita do usuário.
- Não simular timeout, `429`, `5xx`, payload inválido, página vazia ou mudança de seletor como etapa obrigatória.
- Validar a extração durante a reprodução local do flow completo. Quando ocorrer uma falha real, diagnosticar pelos logs, corrigir e executar o flow novamente até terminar sem falhas.
