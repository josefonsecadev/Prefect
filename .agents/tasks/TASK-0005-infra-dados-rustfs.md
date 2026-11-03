# TASK-0005 — Migrar infraestrutura e dados para RustFS

## Identificação

- Status: backlog
- Categoria: docker
- Tipo: manutencao
- Etiquetas: [infraestrutura, rustfs, s3, lakekeeper, iceberg, migracao]
- Prioridade: P2
- Complexidade: TEM QUE PENSAR
- Origem: RustFS como padrão sem perder funcionamento ou dados existentes.
- Criada em: 2026-11-03
- Atualizada em: 2026-11-03
- Dependências: TASK-0003 e TASK-0004 concluídas.

## Objetivo, contexto e limites

Subir RustFS, provisionar buckets, preservar dados e atualizar Lakekeeper para o
novo endpoint, mantendo os demais serviços e versões. Compose atual usa MinIO,
`minio/mc`, volume `D:/Dados` e bootstrap que aceita 409 sem reconciliar warehouse.
Referências: `docker-compose.yml`, `Dockerfile`, `.env.example`, contrato em TASK-0003.

Não montar diretório interno MinIO no RustFS; usar volume novo. Não recriar warehouse,
apagar snapshots, alterar schema nem executar `docker compose down -v`. `.env`
real fica local e nunca é versionado. Preservar origem até aceite final e política
posterior de retenção; esta demanda não autoriza exclusão do armazenamento antigo.

## Etapas

Cada etapa inclui este arquivo e índice; no máximo três outros arquivos, cinco no
total. Estimativas até 5.000 tokens incluem revisão e evidências. Tempo de cópia
pode ser maior que o tempo de interação; acompanhar operações sem inventar sucesso.

### E01 — Serviço RustFS e bootstrap S3

- Status: backlog.
- Estimativa: 4.000 tokens.
- Arquivos: `docker-compose.yml`, `.env.example`, `Dockerfile` se necessário + controle (até cinco).
- Ações: fixar imagem/digest decidido, configurar persistência e permissões,
  credenciais, portas API/console, healthcheck de prontidão e dependências.
  Substituir bootstrap MinIO por operação S3 idempotente definida em TASK-0003.
  Preservar buckets `bronze`, `prata`, `ouro`, `iceberg` e prefixos existentes.
- Preparar migração com MinIO antigo acessível de forma temporária e RustFS em
  porta alternativa; não iniciar worker/escritas no novo destino antes de E03.
  Se precisar de arquivo Compose temporário versionado, dividir etapa antes de exceder o limite.
- Evidência: configuração revisada, comandos de inicialização definidos; prontidão
  da infraestrutura não é aceite de flow e não substitui TASK-0006.
- Resultado: pendente.

### E02 — Reconciliar o warehouse Lakekeeper

- Status: backlog; depende de E01.
- Estimativa: 4.000 tokens.
- Arquivos: `docker-compose.yml`, helper de bootstrap se necessário + controle (até quatro).
- Ações: implementar criação para ambiente novo e reconciliação via API suportada
  para ambiente existente. Comparar endpoint/perfil e credenciais sem registrar
  segredos. Manter bucket, key-prefix, warehouse, catálogo, UUIDs e localizações.
  Não assumir que `flavor=minio` é correto para RustFS; seguir contrato confirmado.
- Desabilitar STS conforme uso atual; erros de autenticação, perfil e API devem
  falhar com contexto. Um 409 não comprova configuração correta. Aplicar mudança
  em ambiente com dados somente após sincronização final em E03.
- Evidência: caminhos de criação e atualização documentados, sem corte antecipado.
- Resultado: pendente.

### E03 — Copiar objetos e efetuar o corte

- Status: backlog; depende de E01/E02 e inventário da TASK-0003.
- Estimativa: 4.500 tokens.
- Arquivos: este registro, índice e `docker-compose.yml` para configuração definitiva (até três).
- Ações: aplicar procedimento definido: cópia inicial S3, pausar todos os escritores
  (worker, agendamentos e execuções locais), confirmar ausência de execuções ativas,
  sincronizar novamente sem remoções e gerar evidência de integridade.
- Conferir conjunto de chaves e bytes por bucket, conteúdo/checksums quando disponíveis;
  ETag de multipart não é necessariamente hash do conteúdo. Incluir todos os arquivos
  referenciados pelos snapshots, não só os dados do snapshot atual. Inventário vazio
  comprovado permite registrar cópia como não aplicável, sem presumir que não há dados.
- Efetuar backup consistente do estado do catálogo e preservar sua chave de criptografia
  de forma segura; não copiar nem publicar segredos no registro.
- Atualizar perfil/credenciais do catálogo e endpoint dos clientes; retirar servidor
  MinIO e bootstrap antigo do caminho padrão. Manter cópia antiga preservada.
- Registrar condições de retorno antes e depois de novas escritas; nunca apontar
  catálogo atualizado para um destino sem os objetos referenciados.
- Evidência: manifesto/resumo de cópia sem dados privados, contagens, bytes,
  estado do catálogo e procedimento de rollback. Liberar validação em TASK-0006.
- Resultado: pendente.

## Critérios de aceite

- [ ] RustFS é servidor padrão; bootstrap idempotente e prontidão correta.
- [ ] Migração preserva objetos, localizações e snapshots, com evidência de integridade.
- [ ] Warehouse existente reconciliado e ambiente novo também suportado.
- [ ] Volumes antigos preservados; rollback definido; sem atualização de serviços alheios.
- [ ] Ambiente pronto para flows completos; funcionamento final depende de TASK-0006.

## Retomada e histórico

- Próxima ação: após dependências, revisar contrato e executar E01.
- Feito: planejamento somente; nenhum container, volume ou dado foi alterado.
- Bloqueios: dependências e acesso ao ambiente/inventário antes do corte.
- Validação pendente: flows e snapshots em TASK-0006.
- 2026-11-03 — tarefa registrada com preservação obrigatória e etapas estimadas.
