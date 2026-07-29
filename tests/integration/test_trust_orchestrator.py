#!/usr/bin/env python3
"""
EAML-PT Contract Testing - Testes do Orquestrador de Confiança
Garante o princípio de 'Fail-Closed' e a execução obrigatória de 'Zeroization'
(limpeza de memória RAM) em qualquer cenário de sucesso ou falha.
"""

import unittest
from unittest.mock import MagicMock
import sys
import os

# Adiciona a raiz do projeto ao path para importar o orquestrador
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../core')))

from trust_orchestrator import TrustOrchestrator

class TestTrustOrchestrator(unittest.TestCase):
    
    def setUp(self):
        """Prepara o orquestrador e substitui os módulos externos por Mocks para isolar o teste."""
        self.orchestrator = TrustOrchestrator()
        
        # Injeção de dependências simuladas (Mocks)
        self.orchestrator.attestation_client = MagicMock()
        self.orchestrator.hsm_broker = MagicMock()
        self.orchestrator.ebsi_notary = MagicMock()
        self.orchestrator.oversight_gateway = MagicMock()

    def test_successful_governance_transaction(self):
        """Valida o "Caminho Feliz" - Sucesso de ponta a ponta e limpeza de memória no final."""
        # Configurar comportamento esperado dos mocks
        self.orchestrator.attestation_client.get_attestation_token.return_value = "mock_token_123"
        mock_pqc_key = bytearray(b"MOCK_PQC_KEY_768")
        self.orchestrator.hsm_broker.fetch_operational_keys.return_value = mock_pqc_key
        self.orchestrator.oversight_gateway.evaluate_decision.return_value = {"status": "APPROVED"}
        self.orchestrator.ebsi_notary.create_evidence_hash.return_value = "hash_ebsi_001"
        self.orchestrator.ebsi_notary.anchor_to_ledger.return_value = True

        # Executar a transação
        result = self.orchestrator.execute_governance_transaction("ctx-test-001", 0.20, {"service": "test"})

        # Verificações de integridade
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["decision"], "APPROVED")
        
        # VALIDAÇÃO CRÍTICA: A chave tem de ter sido destruída no final (Zeroization)
        self.orchestrator.hsm_broker.secure_zeroize.assert_called_once_with(mock_pqc_key)

    def test_fail_closed_on_ebsi_failure(self):
        """Valida o princípio de Fail-Closed e Zero-Storage caso a rede Blockchain (EBSI) falhe."""
        # Configurar comportamento esperado dos mocks
        self.orchestrator.attestation_client.get_attestation_token.return_value = "mock_token_123"
        mock_pqc_key = bytearray(b"MOCK_PQC_KEY_768")
        self.orchestrator.hsm_broker.fetch_operational_keys.return_value = mock_pqc_key
        self.orchestrator.oversight_gateway.evaluate_decision.return_value = {"status": "APPROVED"}
        self.orchestrator.ebsi_notary.create_evidence_hash.return_value = "hash_ebsi_002"
        
        # Forçar falha no registo EBSI
        self.orchestrator.ebsi_notary.anchor_to_ledger.return_value = False

        # Executar a transação
        result = self.orchestrator.execute_governance_transaction("ctx-test-002", 0.20, {"service": "test"})

        # Verificações de segurança (Fail-Closed)
        self.assertEqual(result["status"], "FAILED")
        
        # VALIDAÇÃO CRÍTICA: Mesmo com falha, a chave PQC TEM de ser destruída da RAM (Zeroization)
        self.orchestrator.hsm_broker.secure_zeroize.assert_called_once_with(mock_pqc_key)

if __name__ == "__main__":
    unittest.main()
