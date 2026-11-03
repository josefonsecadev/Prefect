# TASK-0007 — Escolher arquitetura de acesso SQL à Ouro

## Identificação

- Status: concluida
- Categoria: infraestrutura
- Tipo: investigacao
- Etiquetas: [ouro, trino, polaris, rustfs, iceberg, arquitetura]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: usuário escolheu explicitamente Trino + Polaris, com ambiente novo.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: nenhuma para a decisão; implementação em TASK-0003 a TASK-0009.

## Decisão e escopo

RustFS armazena objetos, Polaris é o catálogo REST Iceberg e Trino oferece SQL
somente leitura da Ouro. Prefect orquestra; DuckDB transforma e publica pelo Polaris.
Lakekeeper sai da arquitetura alvo. Trino não substitui DuckDB nas transformações.
Não há migração de objetos, snapshots, UUIDs, identidades ou registros de catálogo;
novos volumes, catálogo, grants e dados serão criados do zero.

A arquitetura está registrada em `.agents/knowledge/planning.md`. A escolha está
encerrada; limites operacionais e versões são entregas da TASK-0003, não motivo
para reabrir a comparação de produtos. Nenhum componente foi implantado nesta task.

## Etapas e evidências

### E01 — Comparar engines e catálogos

- Status: concluida; estimativa original: 4.000 tokens.
- Evidência: comparação apresentada no chat entre Trino, Doris, Spark e catálogos;
  [guia oficial Polaris/Trino/RustFS](https://polaris.apache.org/guides/trino/).
- Resultado: Trino + Polaris escolhidos pelo usuário; integração local ainda não validada.

### E02 — Registrar arquitetura aprovada e desdobrar execução

- Status: concluida; estimativa: 3.500 tokens.
- Arquivos desta entrega: este registro, índice, TASK-0006, TASK-0008 e TASK-0009 (cinco).
  Contratos e base de infraestrutura foram revisados na entrega documental anterior
  (planning, índice, TASK-0003, TASK-0004 e TASK-0005; cinco arquivos).
- Resultado: arquitetura alvo e dependências registradas, escopo de migração descartado.
- Evidência: registros locais revisados; limite por etapa e dependências conferidos
  no QA documental; sem alegar validação executável da futura stack.

## Critérios de aceite

- [x] Engine e catálogo escolhidos explicitamente pelo usuário.
- [x] Arquitetura e decisão de partir do zero registradas.
- [x] Tasks de implementação, acesso restrito e validação criadas.

## Retomada e histórico

- Próxima ação: TASK-0003/E01; depois base e código, Trino e consumo Ouro.
- Validações futuras: TASK-0006 e TASK-0009; esta conclusão é da decisão, não da implantação.
- 2026-11-03 — inicialmente Trino era candidato com Lakekeeper mantido.
- 2026-11-03 — usuário autorizou avaliar outros catálogos; Polaris, Gravitino e Nessie considerados.
- 2026-11-03 — usuário escolheu Trino + Polaris e dispensou migração de dados/catálogos;
  comparação encerrada, implementação desdobrada nas tasks.
