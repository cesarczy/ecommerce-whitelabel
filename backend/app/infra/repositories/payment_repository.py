from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.ports import PaymentRepository
from app.core.context.tenant import get_current_tenant_id
from app.core.middlewares.tenant import DEFAULT_TENANT_ID
from app.domain.payments.entities.payment import Payment, PaymentMethod, PaymentProvider, PaymentStatus
from app.domain.shared.entity_id import EntityId
from app.domain.shared.value_objects.money import Money
from app.infra.models.models import PaymentModel


def _tenant_id() -> UUID:
    return get_current_tenant_id() or DEFAULT_TENANT_ID


def _to_domain(model: PaymentModel) -> Payment:
    return Payment.reconstitute(
        payment_id=EntityId.from_string(str(model.id)),
        order_id=EntityId.from_string(str(model.order_id)),
        amount=Money(model.amount_cents, model.currency),
        method=PaymentMethod(model.method),
        provider=PaymentProvider(model.provider),
        status=PaymentStatus(model.status),
        external_id=model.external_id,
        checkout_url=model.checkout_url,
        metadata=dict(model.payment_metadata or {}),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyPaymentRepository(PaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, payment: Payment) -> None:
        result = await self._session.execute(select(PaymentModel).where(PaymentModel.id == payment.id.value))
        model = result.scalar_one_or_none()
        if model is None:
            model = PaymentModel(id=payment.id.value, tenant_id=_tenant_id(), order_id=payment.order_id.value)
            self._session.add(model)
        model.amount_cents = payment.amount.amount_cents
        model.currency = payment.amount.currency
        model.method = payment.method.value
        model.provider = payment.provider.value
        model.status = payment.status.value
        model.external_id = payment.external_id
        model.checkout_url = payment.checkout_url
        model.payment_metadata = payment.metadata
        model.created_at = payment.created_at
        model.updated_at = payment.updated_at
        await self._session.flush()

    async def find_by_id(self, payment_id: UUID) -> Payment | None:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id, PaymentModel.tenant_id == _tenant_id())
        )
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def find_by_order_id(self, order_id: UUID) -> Payment | None:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.order_id == order_id, PaymentModel.tenant_id == _tenant_id())
        )
        model = result.scalars().first()
        return _to_domain(model) if model else None

    async def find_by_external_id(self, external_id: str) -> Payment | None:
        result = await self._session.execute(
            select(PaymentModel).where(
                PaymentModel.external_id == external_id,
                PaymentModel.tenant_id == _tenant_id(),
            )
        )
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None
