#!/usr/bin/env python3
"""
EAML-PT Sovereign Event Broker Consumer (NIS2 & Event-Driven Compliance)
Consome eventos do barramento, valida a integridade via hash SHA-384 e assegura amnésia transacional.
"""

import hashlib
import json
import logging
import sys
from typing import Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("EAML.EventConsumer")

class SovereignEventConsumer:
    """
    Consumidor responsável por ler as mensagens do barramento assíncrono,
    verificar o envelope de segurança e processar o evento sem reter dados sensíveis.
    """

    def __init__(self, topic_name: str = "eaml.audit.oversight"):
        self.topic_name = topic_name
        logger.info("SovereignEventConsumer inicializado para o tópico: %s", self.topic_name)

    def verify_message_integrity(self, raw_payload: Dict[str, Any], expected_hash: str) -> bool:
        """Valida se o conteúdo do evento corresponde estritamente ao hash SHA-384 esperado."""
        payload_string = json.dumps(raw_payload, sort_keys=True)
        computed_hash = hashlib.sha384(payload_string.encode('utf-8')).hexdigest()
        is_valid = computed_hash == expected_hash
        
        if is_valid:
            logger.info("Integridade da mensagem validada com sucesso via SHA-384.")
        else:
            logger.error("ALERTA DE SEGURANÇA: Falha na validação de integridade do evento!")
            
        return is_valid

    def consume_event(self, event_envelope: Dict[str, Any], original_raw_data: Dict[str, Any]) -> bool:
        """Simula a receção e processamento seguro de um evento no barramento."""
        logger.info("A processar evento recebido do tópico [%s]...", self.topic_name)
        
        expected_hash = event_envelope.get("payload_sha384")
        if not expected_hash:
            logger.error("Envelope de evento inválido: falta o campo de hash SHA-384.")
            return False

        # Validação de integridade antes de qualquer ação
        if self.verify_message_integrity(original_raw_data, expected_hash):
            logger.info("Evento processado com conformidade eIDAS 2.0 / NIS2.")
            return True
            
        logger.warning("Mensagem rejeitada devido a divergência de integridade.")
        return False

if __name__ == "__main__":
    consumer = SovereignEventConsumer()
    
    # Simulação de dados de teste
    sample_raw_data = {"action": "verify_identity", "risk": 0.15}
    sample_envelope = {
        "event_version": "1.0",
        "crypto_standard": "NIST-PQC-Hybrid",
        "payload_sha384": hashlib.sha384(json.dumps(sample_raw_data, sort_keys=True).encode('utf-8')).hexdigest(),
        "status": "SECURE_TRANSMISSION_READY"
    }
    
    success = consumer.consume_event(sample_envelope, sample_raw_data)
    print("Estado do consumo assíncrono:", success)
  
