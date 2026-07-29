#!/usr/bin/env python3
"""
EAML-PT API Gateway - Ponto de Entrada Seguro (Atualizado)
Exposição RESTful utilizando FastAPI. Valida a EUDI Wallet (eIDAS) 
e orquestra a transação de governação garantindo Zero-Storage.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import sys
import os
import logging
import time

# Configuração de caminhos para os módulos do core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../core')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../identity')))

try:
    from trust_orchestrator import TrustOrchestrator
    from eidas_validator import EidasCredentialValidator
except ImportError as e:
    logging.error(f"Erro ao carregar módulos no API Gateway: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] API_GATEWAY: %(message)s')

# Instâncias Globais (Carregadas no arranque)
orchestrator = TrustOrchestrator()
eidas_validator = EidasCredentialValidator()

app = FastAPI(title="EAML-PT API Gateway", version="1.1.0")

# Modelos de Dados (Validação Estrita)
class CredentialValidationRequest(BaseModel):
    context_id: str = Field(..., description="ID único do contexto/transação")
    vp_token: str = Field(..., description="Verifiable Presentation (Payload) enviada pela EUDI Wallet")
    challenge: str = Field(..., description="Nonce/Challenge para evitar Replay Attacks")
    risk_score_override: float | None = Field(default=0.2, description="Score de risco")

class ValidationResponse(BaseModel):
    status: str
    transaction_id: str
    credential_type: str | None = None
    decision: str | None = None
    ebsi_hash: str | None = None
    latency_ms: float

@app.get("/health", tags=["Infraestrutura"])
async def health_check():
    return {"status": "ONLINE", "enclave": "SECURED", "service": "EAML-PT Gateway"}

@app.post("/api/v1/identity/verify", response_model=ValidationResponse, tags=["Soberania eIDAS 2.0"])
async def verify_credential(request: CredentialValidationRequest):
    start_time = time.time()
    logging.info(f"Contexto: {request.context_id} - A iniciar validação eIDAS 2.0...")
    
    # 1. Validação Criptográfica da EUDI Wallet (Fronteira eIDAS)
    eidas_result = eidas_validator.verify_wallet_presentation(request.vp_token, request.challenge)
    
    if eidas_result["status"] == "INVALID":
        logging.error(f"Rejeição na fronteira eIDAS: {eidas_result.get('error')}")
        raise HTTPException(status_code=400, detail=f"Invalid EUDI Presentation: {eidas_result.get('error')}")
        
    cred_type = eidas_result["credential_type"]
    claims = eidas_result["claims_extracted"]
    logging.info(f"eIDAS validado ({cred_type}). A invocar Orquestrador de Confiança...")

    # 2. Orquestração de Governação (TEE -> HSM -> AI Act -> EBSI)
    # ZERO-STORAGE: Passamos ao orquestrador apenas metadados e a contagem de claims, NUNCA os dados pessoais.
    context_data = {
        "service": "api_gateway_crossborder",
        "credential_type": cred_type,
        "claims_processed": len(claims) 
    }

    try:
        gov_result = orchestrator.execute_governance_transaction(
            context_id=request.context_id,
            risk_score=request.risk_score_override,
            context_data=context_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Governance Error")

    end_time = time.time()
    latency_ms = round((end_time - start_time) * 1000, 2)

    if gov_result.get("status") == "FAILED":
        raise HTTPException(status_code=403, detail=f"Governance Failed: {gov_result.get('error')}")

    # A este ponto, todas as variáveis locais contendo 'claims' preparam-se para ser varridas da memória (Garbage Collection)
    return ValidationResponse(
        status=gov_result["status"],
        transaction_id=gov_result["context_id"],
        credential_type=cred_type,
        decision=gov_result.get("decision"),
        ebsi_hash=gov_result.get("ebsi_hash"),
        latency_ms=latency_ms
    )
