"""
Contract Generator Service
Uses GLM AI to generate professional contracts
"""
import os
import httpx
from typing import Dict, Any, Optional
from ..models.schemas import ContractResponse, PaymentStatus


class ContractGenerator:
    """AI-powered contract generator using GLM"""
    
    def __init__(self):
        self.api_key = os.getenv("GLM_API_KEY")
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.mercado_pago_url = "https://api.mercadopago.com/v1/payments"
        
    async def generate(
        self,
        contract_type: str,
        parties: list,
        terms: str,
        additional_context: Optional[str] = None
    ) -> ContractResponse:
        """Generate a contract using AI"""
        
        # Build the prompt
        prompt = self._build_prompt(contract_type, parties, terms, additional_context)
        
        # Call GLM API
        try:
            response = await self._call_glm(prompt)
        except Exception as e:
            # Fallback for demo purposes
            response = self._generate_demo_contract(contract_type, parties, terms)
        
        return ContractResponse(
            contract_text=response,
            contract_type=contract_type,
            parties=parties,
            status="generated"
        )
    
    def _build_prompt(
        self,
        contract_type: str,
        parties: list,
        terms: str,
        additional_context: Optional[str]
    ) -> str:
        """Build the system prompt for contract generation"""
        
        base_prompt = f"""Eres un abogado experto en contratos comerciales. 
Genera un contrato profesional de tipo '{contract_type}' con las siguientes partes:

Partes involucradas:
{chr(10).join(f"- {p}" for p in parties)}

Términos y condiciones:
{terms}

"""
        
        if additional_context:
            base_prompt += f"\nContexto adicional:\n{additional_context}\n"
        
        base_prompt += """
Genera un contrato completo y profesional en español o inglés (elige el más apropiado).
Incluye:
- Título del contrato
- Partes identificables
- Definiciones
- Obligaciones de cada parte
- Plazos y condiciones
- Cláusulas de confidencialidad
- Ley aplicable
- Firmas

Formato: Documento legal profesional."""
        
        return base_prompt
    
    async def _call_glm(self, prompt: str) -> str:
        """Call GLM API to generate contract"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "glm-4",
            "messages": [
                {"role": "system", "content": "Eres un asistente legal experto que genera contratos profesionales."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"GLM API error: {response.status_code}")
    
    def _generate_demo_contract(
        self,
        contract_type: str,
        parties: list,
        terms: str
    ) -> str:
        """Generate a demo contract when API is not available"""
        
        return f"""
{contract_type.upper()} CONTRACT

This Agreement is entered into by and between:

{parties[0] if parties else "Party A"}
and
{parties[1] if len(parties) > 1 else "Party B"}

TERMS AND CONDITIONS:
{terms}

CONFIDENTIALITY CLAUSE:
All information exchanged between the parties shall remain confidential and shall not be disclosed to third parties without prior written consent.

GOVERNING LAW:
This Agreement shall be governed by and construed in accordance with applicable laws.

IN WITNESS WHEREOF, the parties have executed this Agreement.

_______________________          _______________________
{parties[0] if parties else "Party A"}           {parties[1] if len(parties) > 1 else "Party B"}
Date: _______________          Date: _______________
"""
    
    async def create_payment(self, amount: float, currency: str) -> PaymentStatus:
        """Create a payment via Mercado Pago"""
        # This would integrate with Mercado Pago API
        # For now, return a demo payment status
        return PaymentStatus(
            payment_id="demo_payment_123",
            status="pending",
            checkout_url="https://www.mercadopago.com/checkout/demo"
        )
