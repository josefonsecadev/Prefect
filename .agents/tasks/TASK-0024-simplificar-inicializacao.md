# TASK-0024 — Separar instalação e operação

- Status: concluida
- Categoria: infraestrutura
- Tipo: melhoria
- Prioridade: P2
- Origem: usuário, 2026-11-05; trabalhar na main.

## Contrato e etapas
Preservar dados, credenciais e autenticação TLS/SQL. Configuração estática do Trino
versionada; segredos no .env e certificado/hash local ignorado. Polaris emite suas
credenciais: preservar as atuais, sem rotação. Instalação explícita no host prepara
buckets, catálogo e permissões; inicialização diária não executa provisionamento.

1. Registrar contrato, retirar configuração estática do gerador, em lotes de até
   cinco arquivos. Configuração do Trino permanece equivalente à atual.
2. Separar preparação local de TLS/hash e provisionamento; centralizar credenciais.
3. Ajustar Compose e documentação; validar serviços reais, OAuth e SQL autenticado.
   Se Config compartilhada mudar, executar um orquestrador real em debug.

## Aceite
Compose inicia sem lakehouse-setup automático; Trino saudável com autenticação e
mesmas restrições; credenciais vigentes preservadas. Não executar cargas simultâneas.
Graphify CLI indisponível nesta sessão; leitura direcionada utilizada.

## Evidências de implementação e validação
- Configuração estática extraída em lotes: cinco arquivos properties/JVM/node,
  depois catálogo e ACL. Segredos substituídos por referências ENV.
- bootstrap.py substituído por provision.py (host, manual) e prepare_trino.py
  (TLS/hash SQL de instalação). Launcher shell removido; entrypoint oficial Trino.
- Compose sem lakehouse-setup; polaris-bootstrap restrito ao profile installation.
- Credenciais vigentes writer/reader preservadas no .env; Config não carrega mais
  arquivos intermediários. S3_INTERNAL_ENDPOINT e segredo interno Trino fixados.
- Provisionamento real autenticou ambas as identidades, preservando recursos.
- Falha 401 causal corrigida: Trino 484 requer PBKDF2WithHmacSHA1, gerador anterior
  usava SHA256. Senha preservada; apenas representação hash corrigida.
- SQL real: SELECT current_user=analista; SHOW SCHEMAS FROM ouro retorna somente
  ouro_camara_deputados; listagem de tabelas Ouro funciona (vazia), Prata negada.
  Requisição sem autenticação=401. Grant NAMESPACE_LIST no catálogo permite
  navegação, sem conceder leitura de dados fora da Ouro.
- Flow real com módulo/perfil debug de Legislaturas (Parquet) Completed:
  b4c36db0-09f4-4938-9399-841246783485; 57 registros Bronze/Prata publicados e relidos.
  Log ignorado: .prefect/runtime/flow-simplificacao.log. Não valida escrita Iceberg.
- Build da imagem do worker aprovado; logs locais em runtime. Registro de
  deployments concluído e worker ProcessWorker 1d14ee63-4781-4a0d-b2ab-0c78cf8f72cc
  iniciado. Server preservado ativo; Trino healthy após recriação.
- Compose config --quiet e diff --check aprovados; busca de valores secretos
  do .env nos arquivos versionáveis não encontrou exposição.

## Encerramento
QA aprovada para simplificação em ambiente existente, OAuth e SQL autenticado.
Instalação em volumes vazios não reproduzida para preservar os dados atuais.
Ouro não contém tabelas Iceberg neste ambiente; nenhuma publicação Ouro inventada.
Não houve rotação de credenciais, alteração de negócio ou push. Próximo passo:
operação normal com docker compose --profile processing up -d; comandos de
provisionamento e preparação somente na instalação/manutenção correspondente.
