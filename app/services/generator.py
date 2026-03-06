"""
Contract Generator Service
Uses MiniMax AI to generate professional contracts
Integrates with Mercado Pago and PayPal for payments
"""
import os
import base64
import httpx
import uuid
from typing import Optional
from ..models.schemas import ContractResponse, PaymentStatus


class ContractGenerator:
    """AI-powered contract generator using MiniMax"""

    def __init__(self):
        # MiniMax API - use MINIMAX_API_KEY or ZAI_API_KEY as fallback
        self.api_key = os.getenv("MINIMAX_API_KEY") or os.getenv("ZAI_API_KEY")
        self.api_url = "https://api.minimax.chat/v1/text/chatcompletion_pro"
        self.model = "MiniMax-Text-01"
        
        # Payment providers
        self.mercado_pago_token = os.getenv("MERCADO_PAGO_KEY") or os.getenv("MERCADO_PAGO_ACCESS_TOKEN")
        self.paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.paypal_secret = os.getenv("PAYPAL_SECRET")
        self.paypal_base_url = os.getenv(
            "PAYPAL_API_URL", "https://api-m.sandbox.paypal.com"
        )

    async def generate(
        self,
        contract_type: str,
        parties: list,
        terms: str,
        additional_context: Optional[str] = None,
    ) -> ContractResponse:
        """Generate a contract using MiniMax AI"""
        prompt = self._build_prompt(contract_type, parties, terms, additional_context)

        if not self.api_key:
            contract_text = self._generate_demo_contract(contract_type, parties, terms)
            status = "demo"
        else:
            try:
                contract_text = await self._call_minimax(prompt)
                status = "generated"
            except Exception as e:
                print(f"Minimax error: {e}")
                contract_text = self._generate_demo_contract(contract_type, parties, terms)
                status = "demo_fallback"

        return ContractResponse(
            contract_text=contract_text,
            contract_type=contract_type,
            parties=parties,
            status=status,
        )

    def _build_prompt(
        self,
        contract_type: str,
        parties: list,
        terms: str,
        additional_context: Optional[str],
    ) -> str:
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
Genera un contrato completo y profesional en español.
Incluye:
- Título del contrato
- Partes identificables
- Definiciones
- Obligaciones de cada parte
- Plazos y vigencia
- Claúsulas de resolución de conflictos

Formato: Documento legal profesional.
"""
        return base_prompt

    async def _call_minimax(self, prompt: str) -> str:
        """Call MiniMax API to generate contract"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Eres un abogado experto en redactar contratos legales profesionales. Escribe siempre en español de manera formal y precisa."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def _generate_demo_contract(self, contract_type: str, parties: list, terms: str) -> str:
        """Generate a demo contract when API is unavailable"""
        demo_template = f"""# CONTRATO DE {contract_type.upper()}

**CONTRATO GENERADO EN MODO DEMO**

---

## PARTES

{chr(10).join(f"- {p}" for p in parties)}

---

## TÉRMINOS Y CONDICIONES

{terms}

---

## CLÁUSULAS

1. **Objeto del contrato**: El presente contrato tiene por objeto establecer los términos y condiciones entre las partes antes mencionadas.

2. **Obligaciones de las partes**: Cada parte se compromete a cumplir con las obligaciones derivadas del presente contrato.

3. **Vigencia**: El presente contrato tendrá una vigencia de un (1) año desde la fecha de firma, renovable automáticamente.

4. **Resolución de conflictos**: Cualquier controversia derivada de la interpretación o ejecución del presente contrato será resuelta mediante negociación directa entre las partes.

5. **Ley aplicable**: El presente contrato se regirá por las leyes de la República del Perú.

---

*Este es un contrato de demostración. Para generar un contrato personalizado con IA, configure la API key de MiniMax.*

**Contrato tipo**: {contract_type}
**Fecha de generación**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return demo_template

    # Payment methods remain the same...
    async def create_payment(
        self,
        amount: float,
        currency: str = "USD",
        payment_provider: str = "mercado_pago",
        description: str = "Contract Generator Pro"
    ) -> PaymentStatus:
        """Create a payment link"""
        
        if payment_provider == "paypal":
            return await self._create_paypal_payment(amount, currency, description)
        else:
            return await self._create_mercadopago_payment(amount, currency, description)

    async def _create_mercadopago_payment(self, amount: float, currency: str, description: str) -> PaymentStatus:
        """Create Mercado Pago payment"""
        
        if not self.mercado_pago_token:
            return PaymentStatus(
                payment_id="demo_payment",
                payment_url="https://www.mercadopago.com.pe",
                status="demo",
                provider="mercado_pago"
            )
        
        # Create preference
        preference_data = {
            "items": [{
                "title": description,
                "quantity": 1,
                "unit_price": amount,
                "currency_id": "PEN" if currency == "PEN" else "USD"
            }],
            "back_urls": {
                "success": "https://tu-dominio.com/success",
                "failure": "https://tu-dominio.com/failure"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.mercado_pago_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.mercadopago.com/checkout/preferences",
                headers=headers,
                json=preference_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return PaymentStatus(
                    payment_id=data.get("id", "unknown"),
                    payment_url=data.get("init_point", ""),
                    status="pending",
                    provider="mercado_pago"
                )
            else:
                return PaymentStatus(
                    payment_id="error",
                    payment_url="",
                    status="error",
                    provider="mercado_pago"
                )

    async def _create_paypal_payment(self, amount: float, currency: str, description: str) -> PaymentStatus:
        """Create PayPal payment"""
        
        if not self.paypal_client_id or not self.paypal_secret:
            return PaymentStatus(
                payment_id="demo_paypal",
                payment_url="https://www.paypal.com",
                status="demo",
                provider="paypal"
            )
        
        try:
            # Get access token
            auth_response = await self._get_paypal_token()
            if not auth_response:
                return PaymentStatus(payment_id="error", payment_url="", status="error", provider="paypal")
            
            access_token = auth_response["access_token"]
            
            # Create order
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    },
                    "description": description
                }]
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.paypal_base_url}/v2/checkout/orders",
                    headers=headers,
                    json=order_data,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    approval_url = next(
                        (link["href"] for link in data["links"] if link["rel"] == "approve"),
                        ""
                    )
                    return PaymentStatus(
                        payment_id=data["id"],
                        payment_url=approval_url,
                        status="pending",
                        provider="paypal"
                    )
                    
        except Exception as e:
            print(f"PayPal error: {e}")
            
        return PaymentStatus(
            payment_id="demo_paypal",
            payment_url="https://www.paypal.com",
            status="demo",
            provider="paypal"
        )

    async def _get_paypal_token(self) -> Optional[dict]:
        """Get PayPal access token"""
        
        auth_string = base64.b64encode(
            f"{self.paypal_client_id}:{self.paypal_secret}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"grant_type": "client_credentials"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.paypal_base_url}/v1/oauth2/token",
                headers=headers,
                data=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
        return None
