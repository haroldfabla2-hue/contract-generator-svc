"""
Contract Generator SaaS - Main Application
FastAPI backend for AI-powered contract generation
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from .services.generator import ContractGenerator
from .models.schemas import ContractRequest, ContractResponse, PaymentStatus

app = FastAPI(
    title="Contract Generator AI",
    description="AI-powered contract generation service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize generator
generator = ContractGenerator()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")


@app.post("/api/generate", response_model=ContractResponse)
async def generate_contract(request: ContractRequest):
    """
    Generate a contract based on user input
    """
    try:
        result = await generator.generate(
            contract_type=request.contract_type,
            parties=request.parties,
            terms=request.terms,
            additional_context=request.additional_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/contract-types")
async def get_contract_types():
    """Get available contract types"""
    return {
        "types": [
            {"id": "nda", "name": "NDA", "description": "Non-Disclosure Agreement"},
            {"id": "contractor", "name": "Contractor Agreement", "description": "Independent Contractor Agreement"},
            {"id": "employment", "name": "Employment", "description": "Employment Contract"},
            {"id": "lease", "name": "Lease", "description": "Rental Agreement"},
            {"id": "services", "name": "Services", "description": "Professional Services Agreement"},
        ]
    }


@app.post("/api/payment/initiate")
async def initiate_payment(amount: float, currency: str = "USD"):
    """
    Initiate a payment via Mercado Pago
    """
    try:
        payment = await generator.create_payment(amount, currency)
        return payment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "contract-generator-svc"}
