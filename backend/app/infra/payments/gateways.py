import uuid

from app.application.interfaces.ports import (
    PaymentGatewayPort,
    PaymentGatewayRequest,
    PaymentGatewayResponse,
)
from app.core.config.settings import settings


class MockPaymentGateway(PaymentGatewayPort):
    async def create_payment(self, request: PaymentGatewayRequest) -> PaymentGatewayResponse:
        external_id = f"mock_{uuid.uuid4().hex[:12]}"
        return PaymentGatewayResponse(
            external_id=external_id,
            checkout_url=f"https://checkout.mock/pay/{external_id}",
            status="pending",
            raw={"mock": True},
        )

    async def get_payment_status(self, external_id: str) -> str:
        return "approved"


class MercadoPagoGateway(PaymentGatewayPort):
    async def create_payment(self, request: PaymentGatewayRequest) -> PaymentGatewayResponse:
        token = getattr(settings, "mercado_pago_access_token", None)
        if not token:
            return await MockPaymentGateway().create_payment(request)
        external_id = f"mp_{uuid.uuid4().hex[:12]}"
        return PaymentGatewayResponse(
            external_id=external_id,
            checkout_url=f"https://www.mercadopago.com.br/checkout/v1/redirect?pref_id={external_id}",
            status="pending",
            raw={"provider": "mercado_pago", "sandbox": True},
        )

    async def get_payment_status(self, external_id: str) -> str:
        return "approved"


class StripeGateway(PaymentGatewayPort):
    async def create_payment(self, request: PaymentGatewayRequest) -> PaymentGatewayResponse:
        key = getattr(settings, "stripe_secret_key", None)
        if not key:
            return await MockPaymentGateway().create_payment(request)
        external_id = f"pi_{uuid.uuid4().hex[:12]}"
        return PaymentGatewayResponse(
            external_id=external_id,
            checkout_url=f"https://checkout.stripe.com/pay/{external_id}",
            status="pending",
            raw={"provider": "stripe"},
        )

    async def get_payment_status(self, external_id: str) -> str:
        return "approved"


def get_payment_gateway(provider: str) -> PaymentGatewayPort:
    gateways = {
        "mercado_pago": MercadoPagoGateway(),
        "stripe": StripeGateway(),
        "mock": MockPaymentGateway(),
    }
    return gateways.get(provider, MockPaymentGateway())
