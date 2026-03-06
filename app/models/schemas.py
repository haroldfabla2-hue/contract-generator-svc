"""
Pydantic schemas for contract generator
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ContractRequest(BaseModel):
    contract_type: str = Field(..., description="Type of contract to generate")
    parties: List[str] = Field(..., description="List of parties involved")
    terms: str = Field(..., description="Terms and conditions")
    additional_context: Optional[str] = Field(None, description="Additional context")


class ContractResponse(BaseModel):
    contract_text: str
    contract_type: str
    parties: List[str]
    status: str


class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    contract_type: str = Field(default="general")
    description: Optional[str] = None
    payment_provider: str = Field(
        default="mercado_pago",
        description="Payment provider: 'mercado_pago' or 'paypal'",
    )


class PaymentStatus(BaseModel):
    payment_id: str
    status: str
    checkout_url: Optional[str] = None
    message: Optional[str] = None


class ContractType(BaseModel):
    id: str
    name: str
    description: str
