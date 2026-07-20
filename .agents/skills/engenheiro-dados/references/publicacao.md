# Transformação e publicação analítica

## Bronze para DuckDB

1. Ler objetos Bronze pelo recorte solicitado e preservar a rastreabilidade até a chave de origem.
2. Criar relações DuckDB diretamente de CSV, JSON ou Parquet quando possível.
3. Declarar tipos, nomes, nulabilidade e regras de qualidade; não depender apenas de inferência para contratos estáveis.
4. Projetar somente colunas necessárias e filtrar cedo para reduzir memória e I/O.
5. Parametrizar valores SQL. Validar identificadores estruturais contra uma lista permitida ou regra restrita antes de interpolá-los.
6. Tratar casting inválido conforme contrato: falhar, separar rejeitados ou aplicar valor nulo explicitamente. Não descartar silenciosamente.

## Prata e Ouro

- Prata tipa, padroniza, deduplica e valida sem esconder a linhagem da Bronze.
- Ouro existe somente para um uso de negócio definido e consome preferencialmente a Prata.
- Definir chave natural ou técnica, regra de deduplicação e ordenação determinística.
- Manter métricas de entrada, saída, rejeição e duplicidade para reconciliação.

## Iceberg com Lakekeeper

1. Acessar Iceberg pelo catálogo REST Lakekeeper usando as abstrações compartilhadas do projeto.
2. Manter endpoint, warehouse, credenciais e opções do catálogo em configuração externa.
3. Criar namespace e tabela de forma idempotente quando essa responsabilidade pertencer ao pipeline.
4. Compatibilizar schema de escrita com o contrato da tabela. Tratar evolução de schema como decisão explícita e testada.
5. Escolher partições pelos filtros e recortes frequentes, evitando cardinalidade excessiva. Não particionar apenas por conveniência do arquivo de origem.
6. Publicar por operação transacional. Usar substituição do recorte ou `MERGE` definido pelo contrato; não executar append cego em fluxos reprocessáveis.
7. Registrar identificador do snapshot confirmado, tabela, recorte e contagens. Considerar sucesso somente após o commit no catálogo.
8. Não acessar o PostgreSQL interno do Lakekeeper nem colocar regras de negócio nele.

## Idempotência e falhas

- Calcular o recorte de escrita antes da mutação e impedir predicados vazios ou amplos demais.
- Reexecutar o mesmo recorte deve produzir o mesmo estado lógico, sem duplicar dados.
- Falha antes do commit não pode expor tabela parcialmente atualizada.
- Falha ambígua durante commit exige consultar o estado do catálogo antes de repetir a escrita.
- Concorrência sobre a mesma partição precisa ser impedida, serializada ou tratada com conflito explícito.
- Retry pode envolver leitura e commit transitório, mas não corrige schema incompatível, SQL inválido ou regra de qualidade violada.

## Validação

- Comparar contagens e chaves entre Bronze, Prata e rejeitados.
- Verificar tipos, nulabilidade, unicidade, domínio e limites definidos no contrato.
- Consultar a tabela publicada por meio do catálogo e confirmar o snapshot.
- Reprocessar o mesmo recorte e comparar contagens e chaves.
- Confirmar que partições fora do recorte permaneceram inalteradas.
- Testar payload vazio, schema novo ou ausente, dados duplicados e conflito de commit.
