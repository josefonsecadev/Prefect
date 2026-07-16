# Desenvolvimento Sênior

Guia de execução das alterações definidas pelo planejamento.

## Responsabilidade

O desenvolvimento sênior transforma um planejamento aprovado em uma implementação funcional. Sua responsabilidade começa depois que a arquitetura, o escopo, os contratos e os critérios de aceite foram definidos.

Este knowledge não decide arquitetura. As decisões sobre componentes, camadas, tecnologias, estrutura de pastas, contratos de dados e evolução da solução pertencem ao `.agents/knowledge/planning.md`.

Se a execução exigir uma decisão que não esteja no planejamento, interrompa a alteração e devolva a questão para a etapa de arquitetura. Não complete lacunas arquiteturais por suposição.

## Entradas obrigatórias para execução

Antes de alterar qualquer arquivo, confirme que o planejamento informa:

1. resultado esperado;
2. escopo da etapa;
3. arquivos ou componentes afetados;
4. comportamento que deve ser preservado;
5. critérios de aceite;
6. validações que devem ser executadas.

Se uma dessas informações estiver ausente e puder alterar a solução, solicite a complementação do planejamento.

## Preparação do ambiente

1. Leia o planejamento aprovado para a etapa atual.
2. Leia integralmente os arquivos que serão modificados e seus usos diretos.
3. Verifique o estado do Git antes de editar.
4. Identifique alterações preexistentes e preserve todo conteúdo que não faça parte da demanda.
5. Confirme que a etapa altera no máximo cinco arquivos.
6. Determine os comandos de validação já definidos para a entrega.

Não inicie a implementação enquanto houver conflito entre o planejamento e o estado real do projeto.

## Execução da alteração

Para cada etapa aprovada:

1. Faça a menor alteração capaz de atender ao critério de aceite.
2. Respeite nomes, contratos, caminhos e tecnologias definidos pelo planejamento.
3. Mantenha o estilo predominante nos arquivos próximos.
4. Evite refatorações, formatações ou renomeações sem relação direta com a demanda.
5. Não adicione dependências, serviços, configurações ou abstrações que não estejam previstas.
6. Atualize documentação e exemplos somente quando forem afetados pela mudança.
7. Conclua e valide a etapa antes de iniciar a próxima.

## Práticas de implementação

- Escreva funções e métodos pequenos, com nomes que expressem a ação realizada.
- Use tipagem compatível com a versão de Python declarada pelo projeto.
- Remova duplicação apenas quando isso fizer parte do escopo ou for necessário para implementar corretamente a alteração.
- Valide entradas nos limites definidos pelo contrato recebido.
- Propague falhas com contexto suficiente para localizar a operação que falhou.
- Não capture exceções sem tratamento útil ou apenas para permitir que a execução continue.
- Não exponha credenciais, tokens, variáveis sensíveis ou conteúdo privado em logs e mensagens de erro.
- Use os recursos compartilhados já existentes antes de criar uma nova implementação equivalente.
- Mantenha compatibilidade com as interfaces que o planejamento determinou preservar.
- Comentários devem explicar decisões não evidentes; não devem repetir o código.

## Controle de escopo

Durante a execução, não é responsabilidade do desenvolvedor:

- escolher ou substituir tecnologias;
- redefinir a arquitetura de dados;
- mover responsabilidades entre componentes ou camadas;
- criar novos contratos não previstos;
- alterar infraestrutura como efeito colateral;
- ampliar a demanda porque encontrou uma melhoria possível.

Ao encontrar uma necessidade desse tipo, registre a evidência, explique o impacto sobre a execução e encaminhe a decisão ao planejamento.

Correções pequenas e indispensáveis para concluir a etapa podem ser realizadas somente quando não mudarem o contrato, a arquitetura ou o comportamento fora do escopo. A correção deve ser informada na entrega.

## Execução das validações

O desenvolvedor executa as validações previstas no planejamento e nos critérios de qualidade do projeto. Ele não substitui a avaliação final de qualidade.

1. Execute primeiro a validação mais específica da alteração.
2. Execute depois as verificações de integração indicadas no planejamento.
3. Registre o comando executado e seu resultado.
4. Em caso de falha, corrija apenas problemas causados ou expostos diretamente pela alteração.
5. Revise o diff após ferramentas automáticas para identificar mudanças indevidas.
6. Se uma validação não puder ser executada, informe o motivo e o risco restante.

Não declare sucesso com base apenas em leitura manual, logs sem assertions ou ausência aparente de erros.

## Revisão antes da entrega

Antes de encaminhar a etapa para avaliação:

- confira se todos os critérios de aceite foram atendidos;
- confirme que nenhum arquivo fora do escopo foi alterado;
- procure código temporário, prints, segredos, comentários pendentes e arquivos gerados;
- confira se mensagens de erro e logs possuem contexto sem expor dados sensíveis;
- confirme que as validações executadas correspondem ao risco da mudança;
- revise o diff completo da etapa;
- consulte `.agents/knowledge/qa_chato.md` antes de commit e push, quando o arquivo estiver disponível.

## Entrega da etapa

A entrega deve informar objetivamente:

1. o que foi implementado;
2. quais arquivos foram alterados;
3. quais validações foram executadas e seus resultados;
4. quais riscos ou limitações permanecem;
5. se alguma decisão precisa retornar ao planejamento;
6. se a etapa está pronta para avaliação de qualidade.

O commit deve ser pequeno, descritivo e conter somente a etapa concluída. Commit e push só podem ocorrer depois da avaliação prevista pelo projeto e conforme a autorização e o fluxo Git vigente.

## PASSOS PARA SEGUIR

AO RECEBER UM PLANEJAMENTO APROVADO, EXECUTE UMA ETAPA POR VEZ, ALTERANDO NO MÁXIMO CINCO ARQUIVOS. CONCLUA AS VALIDAÇÕES E A REVISÃO DO DIFF ANTES DE INICIAR A PRÓXIMA ETAPA.

SE A IMPLEMENTAÇÃO EXIGIR UMA NOVA DECISÃO DE ARQUITETURA, INTERROMPA A EXECUÇÃO E DEVOLVA A QUESTÃO AO `planning.md`. NÃO MODIFIQUE A ARQUITETURA DURANTE A CODIFICAÇÃO.

## Checklist de execução concluída

- [ ] O planejamento da etapa estava completo e aprovado.
- [ ] A implementação permaneceu dentro do escopo e do limite de arquivos.
- [ ] Alterações preexistentes foram preservadas.
- [ ] Contratos e decisões recebidos foram respeitados.
- [ ] Nenhuma decisão arquitetural foi tomada durante a execução.
- [ ] As validações previstas foram executadas e registradas.
- [ ] O diff completo foi revisado.
- [ ] Riscos e limitações foram informados.
- [ ] A alteração está pronta para avaliação de qualidade.
