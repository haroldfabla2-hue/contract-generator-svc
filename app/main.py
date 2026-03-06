"""
Contract Generator SaaS - Main Application
FastAPI backend for AI-powered contract generation
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from .services.generator import ContractGenerator
from .models.schemas import ContractRequest, ContractResponse, PaymentRequest, PaymentStatus

app = FastAPI(
    title="Contract Generator AI",
    description="AI-powered contract generation service",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

generator = ContractGenerator()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/generate", response_model=ContractResponse)
async def generate_contract(request: ContractRequest):
    try:
        result = await generator.generate(
            contract_type=request.contract_type,
            parties=request.parties,
            terms=request.terms,
            additional_context=request.additional_context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/contract-types")
async def get_contract_types():
    return {
        "types": [
            {"id": "nda", "name": "NDA", "description": "Acuerdo de Confidencialidad"},
            {"id": "contractor", "name": "Prestación de Servicios", "description": "Contrato de Prestación de Servicios"},
            {"id": "employment", "name": "Empleo", "description": "Contrato de Trabajo"},
            {"id": "lease", "name": "Alquiler", "description": "Contrato de Alquiler"},
            {"id": "services", "name": "Servicios Profesionales", "description": "Contrato de Servicios Profesionales"},
        ]
    }


@app.post("/api/payment/initiate", response_model=PaymentStatus)
async def initiate_payment(request: PaymentRequest):
    try:
        payment = await generator.create_payment(
            amount=request.amount,
            currency=request.currency,
            contract_type=request.contract_type,
            description=request.description or "",
            payment_provider=request.payment_provider,
        )
        return payment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def api_status():
    """Check which integrations are configured"""
    return {
        "glm_configured": bool(os.getenv("GLM_API_KEY") or os.getenv("ZAI_API_KEY")),
        "mercado_pago_configured": bool(os.getenv("MERCADO_PAGO_ACCESS_TOKEN")),
        "paypal_configured": bool(os.getenv("PAYPAL_CLIENT_ID") and os.getenv("PAYPAL_SECRET")),
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "contract-generator-svc", "version": "1.1.0"}
