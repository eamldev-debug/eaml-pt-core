#!/usr/bin/env python3
"""
EAML-PT Trust Infrastructure - Trust Orchestrator
O maestro do Enclave TEE. Orquestra a atestação de hardware, a libertação de chaves HSM,
a avaliação do AI Act e o notariado EBSI de forma atómica e fail-closed.
Garante o princípio estrito de Zero-Storage e limpeza de memória.
"""

import logging
import sys
import os

# Configuração de caminhos para importar os módulos criados nos passos anteriores
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'security')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'blockchain')))

try:
    from attestation_client import ConfidentialAttestationClient
    from hsm_key_release import HSMKeyReleaseBroker
    from ebsi_notary import EBSINotaryClient
    from human_oversight_gateway import HumanOversightGateway
except ImportError as e:
    logging.error(f"Falha ao importar submódulos da infraestrutura de confiança: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("EAML.TrustOrchestrator")

class TrustOrchestrator:
    def __init__(self):
        logger.info("A inicializar Orquestrador de Confiança no Enclave TEE...")
        self.attestation_client = ConfidentialAttestationClient()
        self.hsm_broker = HSMKeyReleaseBroker()
        self.ebsi_notary = EBSINotaryClient()
        self.oversight_gateway = HumanOversightGateway(audit_log_path="in_memory_audit.log", risk_threshold=0.75)

    def execute_governance_transaction(self, context_id: str, risk_score: float, context_data: dict) -> dict:
        """
        Executa o fluxo completo de soberania. Qualquer falha levanta uma exceção (Fail-Closed).
        Garante sempre a zeroization (limpeza de memória) da chave PQC no final.
        """
        logger.info(f"--- A iniciar Transação de Governação para contexto: {context_id} ---")
        operational_key = None

        try:
            # 1. Atestação de Hardware (Prova de Integridade TEE)
            logger.info("[Passo 1/4] A solicitar Atestação de Hardware...")
            attestation_token = self.attestation_client.get_attestation_token()

            # 2. Key Release (Recuperação da Chave PQC para a RAM)
            logger.info("[Passo 2/4] A solicitar libertação de chave ao HSM...")
            operational_key = self.hsm_broker.fetch_operational_keys(attestation_token)

            # 3. Gateway de Supervisão Humana (AI Act Art. 14)
            logger.info("[Passo 3/4] A avaliar risco de governação (AI Act)...")
            decision = self.oversight_gateway.evaluate_decision(context_id, risk_score, context_data)
            
            # 4. Notariado EBSI (Registo Imutável e Zero-Storage)
            logger.info("[Passo 4/4] A ancorar decisão no ledger da EBSI...")
            evidence_hash = self.ebsi_notary.create_evidence_hash(context_id, decision["status"])
            success = self.ebsi_notary.anchor_to_ledger(context_id, evidence_hash, operational_key)

            if not success:
                raise RuntimeError("Falha ao ancorar evidência na EBSI.")

            logger.info(f"--- Transação {context_id} concluída com SUCESSO ---")
            return {
                "status": "SUCCESS",
                "context_id": context_id,
                "ebsi_hash": evidence_hash,
                "decision": decision["status"]
            }

        except Exception as e:
            logger.error(f"TRANSAÇÃO ABORTADA (Fail-Closed ativado). Motivo: {e}")
            return {
                "status": "FAILED",
                "context_id": context_id,
                "error": str(e)
            }

        finally:
            # HIGIENE DE MEMÓRIA MANDATÓRIA (Executada quer a transação falhe ou tenha sucesso)
            if operational_key is not None:
                logger.info("[Segurança] A invocar Zeroization da chave em memória...")
                self.hsm_broker.secure_zeroize(operational_key)
                logger.info("[Segurança] Chave PQC expurgada da RAM com sucesso.")


if __name__ == "__main__":
    # Teste de integração rápido (Dry Run local)
    orchestrator = TrustOrchestrator()
    
    # Simula uma transação de validação de identidade transfronteiriça com baixo risco
    mock_context_data = {"service": "eID_validator_crossborder", "origin": "PT", "target": "ES"}
    resultado = orchestrator.execute_governance_transaction("ctx-eidas-999", 0.15, mock_context_data)
    
    print(f"\nResultado da Orquestração: {resultado}\n")
