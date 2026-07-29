#!/usr/bin/env python3
"""
EAML-PT End-to-End System Integration Tests
Valida o fluxo completo entre produtor, barramento de mensagens e consumidor/gateway,
assegurando conformidade com os SLAs de latência e zero-storage.
"""

import time
import unittest
import sys
import os

# Adiciona a raiz do projeto ao path para importar os módulos de messaging e governance
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from messaging.event_broker_client import SovereignEventProducer
from messaging.event_broker_consumer import SovereignEventConsumer
from human_oversight_gateway import HumanOversightGateway

class TestSystemFlowIntegration(unittest.TestCase):

    def setUp(self):
        """Configuração inicial do ambiente de testes de integração."""
        self.producer = SovereignEventProducer(topic_name="eaml.test.integration")
        self.consumer = SovereignEventConsumer(topic_name="eaml.test.integration")
        self.gateway = HumanOversightGateway(audit_log_path="integration_decisions.log", risk_threshold=0.75)

    def tearDown(self):
        """Limpeza de ficheiros temporários gerados durante os testes."""
        if os.path.exists("integration_decisions.log"):
            os.remove("integration_decisions.log")

    def test_e2e_secure_identity_flow(self):
        """Valida o ciclo completo de ponta a ponta com medição de SLA de latência."""
        start_time = time.time()

        # 1. Simulação de dados de transação de identidade
        context_id = "ctx-integration-test-01"
        risk_score = 0.25
        raw_payload = {"action": "verify_eidas_identity", "level": "high"}

        # 2. Avaliação de decisão pelo Gateway de Supervisão Humana
        gateway_response = self.gateway.evaluate_decision(context_id, risk_score, raw_payload)
        self.assertEqual(gateway_response["status"], "APPROVED")

        # 3. Produção do evento soberano assíncrono
        producer_success = self.producer.publish_event(context_id, raw_payload)
        self.assertTrue(producer_success)

        # 4. Simulação de consumo e validação de integridade no barramento
        secure_envelope = self.producer._sanitize_and_hash_payload(raw_payload)
        consumer_success = self.consumer.consume_event(secure_envelope, raw_payload)
        self.assertTrue(consumer_success)

        # Verificação do SLA de latência (Meta: inferior a 100ms)
        elapsed_time_ms = (time.time() - start_time) * 1000
        print(f"Métrica de Latência E2E: {elapsed_time_ms:.2f}ms")
        self.assertLess(elapsed_time_ms, 100.0, "O fluxo E2E excedeu o SLA máximo de 100ms.")

if __name__ == "__main__":
    unittest.main()
