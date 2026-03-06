"""
Pydantic schemas for contract generator
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ContractRequest(BaseModel):
    """Request model for contract generation"""
    contract_type: str = Field(..., description="Type of contract to generate")
    parties: List[str] = Field(..., description="List of parties involved")
    terms: str = Field(..., description="Terms and conditions")
    additional_context: Optional[str] = Field(None, description="Additional context")


class ContractResponse(BaseModel):
    """Response model for contract generation"""
    contract_text: str
    contract_type: str
    parties: List[str]
    status: str


class PaymentStatus(BaseModel):
    """Payment status model"""
    payment_id: str
    status: str
    checkout_url: Optional[str] = None


class ContractType(BaseModel):
    """Contract type metadata"""
    id: str
    name: str
    description: str
