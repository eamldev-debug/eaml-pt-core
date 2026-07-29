ADR-006: Padrões de Mensajaria Assíncrona com Kafka Sovereignty
​Estado: Aceite
​Data: 2026-03-29
​Contexto Técnico: EAML-PT Core Architecture (NIS2 & eIDAS 2.0 Compliance)
​Contexto e Problema
​As arquiteturas tradicionais de identidade digital baseadas em chamadas síncronas (REST/HTTP) introduzem estrangulamentos transnacionais (HTTP 504) e aumentam o risco de retenção indevida de dados sensíveis de cidadãos nos pontos intermédios de transação, violando os princípios de Zero-Storage e soberania de dados.
​Decisão
​Adotamos um modelo de mensajaria assíncrona baseado em eventos soberanos, implementando o padrão Kafka Sovereignty complementado com as seguintes diretrizes obrigatórias:
​Encriptação Efémera e Hash-Only: Os eventos transmitidos no barramento não contêm dados de identidade em claro. Apenas são transportados metadados e hashes criptográficos SHA-384 (payload_sha384).
​Amnésia Transacional: Tanto os produtores (SovereignEventProducer) quanto os consumidores (SovereignEventConsumer) operam com limpeza estrita de RAM pós-processamento, sem persistência em disco rígido.
​Conformidade Normativa: Alinhamento direto com as diretrizes NIS2 de resiliência operacional e os requisitos de privacidade por omissão do RGPD.
​Consequências
​Positivas: Redução significativa da latência sistémica, eliminação de pontos únicos de falha síncronos e garantia absoluta de proteção de dados por omissão.
​Negativas: Exige maior rigor na monitorização do fluxo assíncrono e na sincronização de contratos de eventos entre microsserviços.
