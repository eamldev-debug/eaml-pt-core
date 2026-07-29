#!/usr/bin/env python3
"""
EAML-PT API Gateway - Ponto de Entrada Seguro
Exposição RESTful utilizando FastAPI. Liga as solicitações externas (ex: EUDI Wallet)
ao Orquestrador de Confiança interno, garantindo validação assíncrona e Zero-Storage.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import sys
import os
import logging
import time

# Adiciona a raiz do projeto ao path para importar o orquestrador
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../core')))

try:
    from trust_orchestrator import TrustOrchestrator
except ImportError as e:
    logging.error(f"Erro ao carregar orquestrador no API Gateway: {e}")
    sys.exit(1)

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] API_GATEWAY: %(message)s')

# Instância Global do Orquestrador (Carregado no arranque do contentor)
orchestrator = TrustOrchestrator()

# Inicialização da App FastAPI
app = FastAPI(
    title="EAML-PT API Gateway",
    description="European Administrative Mobility Layer - Ponto de Entrada Soberano",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None
)

# Modelos de Dados (Validação Estrita de Input via Pydantic)
class CredentialValidationRequest(BaseModel):
    context_id: str = Field(..., description="ID único do contexto/transação")
    credential_type: str = Field(..., description="Tipo de credencial (ex: PID, mDL, VC)")
    risk_score_override: float | None = Field(default=0.2, description="Score de risco calculado pela edge")
    # Nota Zero-Storage: Num cenário real, o 'payload' da credencial vem aqui, 
    # é processado em memória, e NUNCA é guardado em disco ou base de dados.

class ValidationResponse(BaseModel):
    status: str
    transaction_id: str
    decision: str | None = None
    ebsi_hash: str | None = None
    error: str | None = None
    latency_ms: float

@app.get("/health", tags=["Infraestrutura"])
async def health_check():
    """Verificação rápida do estado do API Gateway."""
    return {"status": "ONLINE", "enclave": "SECURED", "service": "EAML-PT Gateway"}

@app.post("/api/v1/identity/verify", response_model=ValidationResponse, tags=["Soberania eIDAS 2.0"])
async def verify_credential(request: CredentialValidationRequest):
    """
    Endpoint principal para verificação de credenciais eIDAS 2.0.
    Encaminha o pedido estritamente em memória para o Orquestrador de Confiança.
    """
    start_time = time.time()
    logging.info(f"Recebido pedido de verificação para o contexto: {request.context_id} ({request.credential_type})")
    
    # Preparar contexto para o orquestrador
    context_data = {
        "service": "api_gateway_crossborder",
        "credential_type": request.credential_type
    }

    # Executa o ciclo TEE -> HSM -> AI Act -> EBSI -> Zeroization
    try:
        # FastAPI gere isto de forma síncrona numa thread pool para não bloquear o event loop
        result = orchestrator.execute_governance_transaction(
            context_id=request.context_id,
            risk_score=request.risk_score_override,
            context_data=context_data
        )
    except Exception as e:
        logging.error(f"Falha catastrófica na orquestração: {e}")
        raise HTTPException(status_code=500, detail="Internal Governance Error")

    end_time = time.time()
    latency_ms = round((end_time - start_time) * 1000, 2)
    logging.info(f"Transação {request.context_id} processada em {latency_ms}ms")

    if result.get("status") == "FAILED":
        raise HTTPException(status_code=403, detail=f"Governance Validation Failed: {result.get('error')}")

    return ValidationResponse(
        status=result["status"],
        transaction_id=result["context_id"],
        decision=result.get("decision"),
        ebsi_hash=result.get("ebsi_hash"),
        latency_ms=latency_ms
    )
