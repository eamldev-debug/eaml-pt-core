#!/usr/bin/env python3
"""
EAML-PT Contract Testing - Validação de Contrato do Gateway de Supervisão
"""

import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from human_oversight_gateway import HumanOversightGateway

class TestHumanOversightGatewayContract(unittest.TestCase):
    
    def setUp(self):
        self.gateway = HumanOversightGateway(audit_log_path="test_decisions.log", risk_threshold=0.75)

    def tearDown(self):
        if os.path.exists("test_decisions.log"):
            os.remove("test_decisions.log")

    def test_contract_structure_low_risk(self):
        response = self.gateway.evaluate_decision("ctx-contract-001", 0.20, {"service": "id_validator"})
        self.assertEqual(response["status"], "APPROVED")
        audit_ref = response["audit_ref"]
        self.assertEqual(len(audit_ref), 96)

    def test_contract_structure_high_risk(self):
        response = self.gateway.evaluate_decision("ctx-contract-002", 0.90, {"service": "infra_modifier"})
        self.assertEqual(response["status"], "ESCALATED")
        audit_ref = response["audit_ref"]
        self.assertEqual(len(audit_ref), 96)

if __name__ == "__main__":
    unittest.main()
