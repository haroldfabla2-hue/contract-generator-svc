"""
Contract Generator Service
Uses GLM AI to generate professional contracts
Integrates with Mercado Pago for payments
"""
import os
import base64
import httpx
import uuid
from typing import Optional
from ..models.schemas import ContractResponse, PaymentStatus


class ContractGenerator:
    """AI-powered contract generator using GLM"""

    def __init__(self):
        self.api_key = os.getenv("GLM_API_KEY") or os.getenv("ZAI_API_KEY")
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.mercado_pago_token = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")
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
        """Generate a contract using GLM AI"""
        prompt = self._build_prompt(contract_type, parties, terms, additional_context)

        if not self.api_key:
            contract_text = self._generate_demo_contract(contract_type, parties, terms)
            status = "demo"
        else:
            try:
                contract_text = await self._call_glm(prompt)
                status = "generated"
            except Exception as e:
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
- Plazos y condiciones
- Cláusulas de confidencialidad
- Ley aplicable
- Firmas

Formato: Documento legal profesional."""
        return base_prompt

    async def _call_glm(self, prompt: str) -> str:
        """Call GLM API to generate contract"""
        if not self.api_key:
            raise ValueError("GLM_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "glm-4",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un asistente legal experto que genera contratos profesionales completos.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60.0,
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(
                    f"GLM API error {response.status_code}: {response.text}"
                )

    def _generate_demo_contract(
        self, contract_type: str, parties: list, terms: str
    ) -> str:
        p1 = parties[0] if parties else "Parte A"
        p2 = parties[1] if len(parties) > 1 else "Parte B"
        return f"""
CONTRATO DE {contract_type.upper()}

Este acuerdo se celebra entre:

{p1}
y
{p2}

TÉRMINOS Y CONDICIONES:
{terms}

CLÁUSULA DE CONFIDENCIALIDAD:
Toda la información intercambiada entre las partes será confidencial y no se divulgará a terceros sin consentimiento previo por escrito.

LEY APLICABLE:
Este contrato se regirá por las leyes aplicables de la jurisdicción correspondiente.

EN FE DE LO CUAL, las partes firman el presente contrato.

_______________________          _______________________
{p1}                              {p2}
Fecha: _______________          Fecha: _______________

⚠️ NOTA: Este es un contrato de demostración. Configure GLM_API_KEY para contratos generados por AI.
"""

    async def create_payment(
        self,
        amount: float,
        currency: str,
        contract_type: str,
        description: str = "",
        payment_provider: str = "mercado_pago",
    ) -> PaymentStatus:
        """Create a payment via Mercado Pago or PayPal"""
        if payment_provider == "paypal":
            return await self._create_paypal_payment(
                amount, currency, contract_type, description
            )
        return await self._create_mercadopago_payment(
            amount, currency, contract_type, description
        )

    async def _create_mercadopago_payment(
        self, amount: float, currency: str, contract_type: str, description: str = ""
    ) -> PaymentStatus:
        """Create a Mercado Pago checkout preference (payment link)"""
        if not self.mercado_pago_token:
            return PaymentStatus(
                payment_id=f"demo_{uuid.uuid4().hex[:8]}",
                status="demo",
                checkout_url=None,
                message="MERCADO_PAGO_ACCESS_TOKEN no configurado. Configure la variable de entorno.",
            )

        headers = {
            "Authorization": f"Bearer {self.mercado_pago_token}",
            "Content-Type": "application/json",
        }

        preference = {
            "items": [
                {
                    "title": f"Contrato Legal - {contract_type}",
                    "description": description or f"Contrato profesional tipo {contract_type}",
                    "quantity": 1,
                    "currency_id": currency.upper(),
                    "unit_price": amount,
                }
            ],
            "back_urls": {
                "success": "https://contract-generator.silhouette.cloud/payment/success",
                "failure": "https://contract-generator.silhouette.cloud/payment/failure",
                "pending": "https://contract-generator.silhouette.cloud/payment/pending",
            },
            "auto_return": "approved",
            "external_reference": f"contract_{uuid.uuid4().hex[:12]}",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mercadopago.com/checkout/preferences",
                    headers=headers,
                    json=preference,
                    timeout=15.0,
                )

                if response.status_code in (200, 201):
                    data = response.json()
                    return PaymentStatus(
                        payment_id=data.get("id", "unknown"),
                        status="created",
                        checkout_url=data.get("init_point"),
                        message="Redirigiendo al checkout de Mercado Pago...",
                    )
                else:
                    return PaymentStatus(
                        payment_id="error",
                        status="error",
                        checkout_url=None,
                        message=f"Error de Mercado Pago: {response.status_code} - {response.text[:200]}",
                    )
        except Exception as e:
            return PaymentStatus(
                payment_id="error",
                status="error",
                checkout_url=None,
                message=f"Error de conexión: {str(e)}",
            )

    async def _get_paypal_access_token(self) -> str:
        """Get OAuth2 access token from PayPal"""
        credentials = base64.b64encode(
            f"{self.paypal_client_id}:{self.paypal_secret}".encode()
        ).decode()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.paypal_base_url}/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data="grant_type=client_credentials",
                timeout=15.0,
            )
            if response.status_code == 200:
                return response.json()["access_token"]
            raise Exception(
                f"PayPal auth error {response.status_code}: {response.text[:200]}"
            )

    async def _create_paypal_payment(
        self, amount: float, currency: str, contract_type: str, description: str = ""
    ) -> PaymentStatus:
        """Create a PayPal checkout order"""
        if not self.paypal_client_id or not self.paypal_secret:
            return PaymentStatus(
                payment_id=f"demo_{uuid.uuid4().hex[:8]}",
                status="demo",
                checkout_url=None,
                message="PAYPAL_CLIENT_ID / PAYPAL_SECRET no configurados. Configure las variables de entorno.",
            )

        try:
            access_token = await self._get_paypal_access_token()

            order_payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "reference_id": f"contract_{uuid.uuid4().hex[:12]}",
                        "description": description
                        or f"Contrato profesional tipo {contract_type}",
                        "amount": {
                            "currency_code": currency.upper(),
                            "value": f"{amount:.2f}",
                        },
                    }
                ],
                "application_context": {
                    "brand_name": "Contract Generator AI",
                    "landing_page": "LOGIN",
                    "user_action": "PAY_NOW",
                    "return_url": "https://contract-generator.silhouette.cloud/payment/success",
                    "cancel_url": "https://contract-generator.silhouette.cloud/payment/failure",
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.paypal_base_url}/v2/checkout/orders",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json=order_payload,
                    timeout=15.0,
                )

                if response.status_code in (200, 201):
                    data = response.json()
                    approve_link = next(
                        (
                            link["href"]
                            for link in data.get("links", [])
                            if link["rel"] == "approve"
                        ),
                        None,
                    )
                    return PaymentStatus(
                        payment_id=data.get("id", "unknown"),
                        status="created",
                        checkout_url=approve_link,
                        message="Redirigiendo al checkout de PayPal...",
                    )
                else:
                    return PaymentStatus(
                        payment_id="error",
                        status="error",
                        checkout_url=None,
                        message=f"Error de PayPal: {response.status_code} - {response.text[:200]}",
                    )
        except Exception as e:
            return PaymentStatus(
                payment_id="error",
                status="error",
                checkout_url=None,
                message=f"Error de conexión PayPal: {str(e)}",
            )
