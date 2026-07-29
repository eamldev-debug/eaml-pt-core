#!/usr/bin/env python3
"""
EAML-PT Human Oversight Gateway (EU AI Act - Art. 14 Compliance)
Garante o fluxo de escalada condicional e auditoria hash-only (SHA-384) para sistemas de IA de alto risco.
"""

import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Configuração de logging estruturado para o ecossistema EAML-PT
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("EAML.OversightGateway")

class HumanOversightGateway:
    """
    Gateway responsável por interceptar decisões de sistemas de IA de alto risco 
    e submetê-las a validação humana condicional quando os limiares de risco são excedidos.
    """

    def __init__(self, audit_log_path: str = "decisions.log", risk_threshold: float = 0.75):
        self.audit_log_path = audit_log_path
        self.risk_threshold = risk_threshold
        logger.info("HumanOversightGateway inicializado com limiar de risco: %s", self.risk_threshold)

    def _generate_sha384_hash(self, payload: Dict[str, Any]) -> str:
        """Regra de Ouro 1: Gera exclusivamente um hash SHA-384 para garantir a amnésia transacional."""
        payload_string = json.dumps(payload, sort_keys=True)
        return hashlib.sha384(payload_string.encode('utf-8')).hexdigest()

    def _write_to_audit_log(self, hashed_record: str) -> None:
        """Escreve estritamente o hash SHA-384 no ficheiro de auditoria, sem dados de identidade em claro."""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = f"{timestamp} | SHA384_HASH: {hashed_record}\n"
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)
            logger.info("Registo de auditoria imutável gravado com sucesso.")
        except IOError as e:
            logger.error("Erro crítico ao escrever no registo de auditoria: %s", e)
            raise

    def evaluate_decision(self, context_id: str, risk_score: float, action_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia se a decisão da IA pode prosseguir automaticamente (Straight-Through Processing)
        ou se exige escalada para supervisão humana (Conditional Escalation).
        """
        logger.info("A avaliar contexto [%s] com score de risco: %s", context_id, risk_score)

        requires_human_review = risk_score >= self.risk_threshold
        decision_status = "PENDING_HUMAN_OVERSIGHT" if requires_human_review else "AUTO_APPROVED"

        audit_payload = {
            "context_id": context_id,
            "risk_score": risk_score,
            "status": decision_status,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "metadata_summary_hash": hashlib.sha256(str(action_metadata).encode()).hexdigest()
        }

        # Aplicação rigorosa da Regra de Ouro 1 (Hash-only)
        record_hash = self._generate_sha384_hash(audit_payload)
        self._write_to_audit_log(record_hash)

        if requires_human_review:
            logger.warning("Decisão suspensa para intervenção humana (Art. 14 EU AI Act). ID: %s", context_id)
            return {
                "status": "ESCALATED",
                "message": "Ação retida para aprovação por operador humano autorizado.",
                "audit_ref": record_hash
            }
        
        logger.info("Decisão aprovada automaticamente por baixo risco. ID: %s", context_id)
        return {
            "status": "APPROVED",
            "message": "Processamento concluído sem restrições de intervenção.",
            "audit_ref": record_hash
        }

if __name__ == "__main__":
    # Teste unitário e sintético básico para validação local
    gateway = HumanOversightGateway()
    
    # Exemplo 1: Abaixo do limiar (Aprovação Automática)
    res_low = gateway.evaluate_decision("ctx-9981-demo", 0.35, {"module": "identity_check"})
    print("Resultado Baixo Risco:", res_low)

    # Exemplo 2: Acima do limiar (Escalada Humana Obrigatória)
    res_high = gateway.evaluate_decision("ctx-9982-demo", 0.88, {"module": "privileged_infra_change"})
    print("Resultado Alto Risco:", res_high)
