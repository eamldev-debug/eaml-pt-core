#!/usr/init/env python3
"""
EAML-PT Contract Testing - Validação de Contrato do Gateway de Supervisão
Garante que o payload e os hashes SHA-384 cumprem o padrão estipulado pela arquitetura.
"""

import unittest
import sys
import os

# Adiciona a raiz do projeto ao path para importar o gateway
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from human_oversight_gateway import HumanOversightGateway

class TestHumanOversightGatewayContract(unittest.TestCase):
    
    def setUp(self):
        """Configuração inicial para cada teste de contrato."""
        self.gateway = HumanOversightGateway(audit_log_path="test_decisions.log", risk_threshold=0.75)

    def tearDown(self):
        """Limpeza de ficheiros temporários gerados durante os testes."""
        if os.path.exists("test_decisions.log"):
            os.remove("test_decisions.log")

    def test_contract_structure_low_risk(self):
        """Valida a estrutura do contrato para um fluxo de baixo risco (Aprovação Automática)."""
        response = self.gateway.evaluate_decision("ctx-contract-001", 0.20, {"service": "id_validator"})
        
        # Verificações de Contrato
        self.assertIn("status", response)
        self.assertIn("audit_ref", response)
        self.assertEqual(response["status"], "APPROVED")
        self.assertEqual(len(response["audit_ref"]), 96)

    def test_contract_structure_high_risk(self):
        """Valida a estrutura do contrato para um fluxo de alto risco (Escalada Condicional)."""
        response = self.gateway.evaluate_decision("ctx-contract-002", 0.90, {"service": "infra_modifier"})
        
        # Verificações de Contrato
        self.assertIn("status", response)
        self.assertIn("audit_ref", response)
        self.assertEqual(response["status"], "ESCALATED")
        self.assertEqual(len(response["audit_ref"]), 96)

if __name__ == "__main__":
    unittest.main()
