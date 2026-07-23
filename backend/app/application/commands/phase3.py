from uuid import UUID

from app.application.commands.cart import _to_order_output
from app.application.dto.schemas import (
    CreateReviewInput,
    OrderOutput,
    PaymentOutput,
    ReviewOutput,
    StoreSettingsOutput,
    UpdateStoreInput,
)
from app.application.exceptions import NotFoundError
from app.application.interfaces.ports import EventBus, UnitOfWork
from app.core.context.tenant import get_current_tenant_id
from app.core.middlewares.tenant import DEFAULT_TENANT_ID
from app.domain.review.entities.review import Review
from app.domain.shared.entity_id import EntityId
from app.domain.store.entities.store_settings import StoreSettings


class ProcessPaymentWebhookUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, *, provider: str, external_id: str, status: str) -> PaymentOutput:
        from app.application.commands.phase2 import _to_payment_output

        payment = await self._uow.payments.find_by_external_id(external_id)
        if payment is None:
            raise NotFoundError("Payment not found")

        if status in ("approved", "paid", "succeeded"):
            payment.approve()
            order = await self._uow.orders.find_by_id(payment.order_id.value)
            if order:
                order.mark_paid(payment.id)
                await self._uow.orders.save(order)
                events = payment.collect_events() + order.collect_events()
            else:
                events = payment.collect_events()
        else:
            payment.reject(status)
            events = payment.collect_events()

        await self._uow.payments.save(payment)
        await self._uow.commit()
        await self._event_bus.publish(events)
        return _to_payment_output(payment)


class ListCustomerOrdersUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, customer_id: UUID) -> list[OrderOutput]:
        orders = await self._uow.orders.find_by_customer_id(customer_id)
        return [_to_order_output(order) for order in orders]


class CreateReviewUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, customer_id: UUID, data: CreateReviewInput) -> ReviewOutput:
        review = Review.create(
            product_id=EntityId.from_string(data.product_id),
            customer_id=EntityId.from_string(str(customer_id)),
            rating=data.rating,
            title=data.title,
            comment=data.comment,
            order_id=EntityId.from_string(data.order_id) if data.order_id else None,
        )
        await self._uow.reviews.save(review)
        events = review.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return ReviewOutput(
            id=str(review.id.value),
            product_id=str(review.product_id.value),
            rating=review.rating,
            title=review.title,
            comment=review.comment,
        )


class UpdateStoreSettingsUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, data: UpdateStoreInput) -> StoreSettingsOutput:
        tenant_id = get_current_tenant_id() or DEFAULT_TENANT_ID
        store = await self._uow.stores.find_by_tenant_id(tenant_id)
        if store is None:
            store = StoreSettings.create(tenant_id=EntityId.from_string(str(tenant_id)), name=data.name or "My Store")
        store.update_branding(
            name=data.name,
            tagline=data.tagline,
            logo_url=data.logo_url,
            primary_color=data.primary_color,
            secondary_color=data.secondary_color,
        )
        await self._uow.stores.save(store)
        events = store.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return StoreSettingsOutput(
            name=store.name,
            tagline=store.tagline,
            logo_url=store.logo_url,
            primary_color=store.primary_color,
            secondary_color=store.secondary_color,
        )
