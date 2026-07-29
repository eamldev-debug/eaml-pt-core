# Evidence Matrix v1.0 - Matriz de Evidências de Governação e Conformidade
* **Projeto:** EAML-PT Core (European Administrative Mobility Layer - Portugal)
* **Estado da Infraestrutura:** READY FOR GOVERNED DRY RUN (Sprint 1)
* **Data de Emissão:** 2026-07-29
* **Classificação:** Relatório de Auditoria Estatal / Conformidade Regulatória
---
## 1. Mapeamento de Conformidade Regulatória

| Regulamento / Norma | Artigo / Requisito | Componente / Ficheiro de Implementação | Métrica / Mecanismo de Validação |
| :--- | :--- | :--- | :--- |
| **EU AI Act** | Art. 14 (Supervisão Humana) | `human_oversight_gateway.py` <br> `tests/contract/test_oversight_gateway_contract.py` | Avaliação automática vs. escalamento condicional por limiar de risco (`risk_threshold=0.75`). |
| **eIDAS 2.0 / NIS2** | Resiliência Operacional & Comunicação Assíncrona | `messaging/event_broker_client.py` <br> `messaging/event_broker_consumer.py` | Barramento soberano desalinhado de chamadas síncronas para eliminação de erros `HTTP 504`. |
| **RGPD** | Art. 25 (Privacidade por Conceção e por Defeito - Zero-Storage) | `docs/adr/adr-006-kafka-sovereignty.md` <br> Encriptação SHA-384 | Transmissão estrita *hash-only* no barramento. Amnésia transacional em RAM sem escrita em disco. |
| **Segurança PQC** | Resistência Ciberquântica (HNDL) | `tests/security/simulate_hndl_interception.py` | Validação de imutabilidade de hashes unidirecionais contra tentativas de engenharia reversa. |
| **SLA de Desempenho** | Latência de Processamento E2E (< 100ms) | `tests/integration/test_system_flow.py` | Testes automáticos de integração medindo a latência do fluxo completo (Gateway + Broker). |
| **Governação Estática** | Validação de Políticas & CI/CD Gating | `policy_checker.py` <br> `.github/workflows/resilience-gate.yml` | Verificação estática automática de ficheiros de configuração em cada *Pull Request*. |

---
## 2. Princípios de Operação Crítica
> **Princípio Fail-Closed:** Em caso de latência extrema no processamento criptográfico pós-quântico ou interrupção na sincronização com os *Trust Anchors* (EBSI / Electronic Ledger), o sistema rejeita automaticamente qualquer transação de elevado risco para proteger a integridade governamental.
---
## 3. Lista de Artefactos de Código Validados
* **Governance & Core:**
  * `policy_checker.py`
  * `human_oversight_gateway.py`
* **Messaging & Sovereignty:**
  * `messaging/event_broker_client.py`
  * `messaging/event_broker_consumer.py`
* **Architecture Decision Records:**
  * `docs/adr/adr-006-kafka-sovereignty.md`
* **Suite de Testes e Segurança:**
  * `tests/contract/test_oversight_gateway_contract.py`
  * `tests/integration/test_system_flow.py`
  * `tests/security/simulate_hndl_interception.py`
