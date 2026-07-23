from uuid import UUID

from app.application.dto.schemas import (
    CheckoutInput,
    CouponOutput,
    CreateCouponInput,
    CreatePaymentInput,
    MfaEnrollOutput,
    MfaVerifyInput,
    OrderOutput,
    PaymentOutput,
    UpdateInventoryInput,
)
from app.application.exceptions import NotFoundError, UnauthorizedError
from app.application.interfaces.ports import (
    EventBus,
    MfaService,
    PaymentGatewayPort,
    PaymentGatewayRequest,
    StoragePort,
    UnitOfWork,
)
from app.application.commands.cart import _to_order_output
from app.domain.coupon.entities.coupon import Coupon, DiscountType
from app.domain.inventory.entities.inventory_item import InventoryItem
from app.domain.payments.entities.payment import Payment, PaymentMethod, PaymentProvider
from app.domain.shared.entity_id import EntityId
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.money import Money
from app.domain.shared.value_objects.sku import SKU
from app.domain.orders.entities.order import Order
from app.infra.repositories.mfa_repository import SqlAlchemyMfaRepository


class CreateCouponUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, data: CreateCouponInput) -> CouponOutput:
        coupon = Coupon.create(
            code=data.code,
            discount_type=DiscountType(data.discount_type),
            discount_value=data.discount_value,
            min_order_cents=int(float(data.min_order_amount) * 100),
            max_uses=data.max_uses,
        )
        await self._uow.coupons.save(coupon)
        events = coupon.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return _to_coupon_output(coupon)


class UpdateInventoryUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, data: UpdateInventoryInput) -> dict:
        item = await self._uow.inventory.find_by_sku(data.sku)
        if item is None:
            item = InventoryItem.create(
                product_id=EntityId.from_string(data.product_id),
                sku=SKU.create(data.sku),
                quantity=data.quantity,
                low_stock_threshold=data.low_stock_threshold,
            )
        else:
            diff = data.quantity - item.quantity_available
            if diff != 0:
                item.adjust(diff)
        await self._uow.inventory.save(item)
        events = item.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return {"sku": str(item.sku), "available": item.quantity_available}


class EnhancedCheckoutUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, customer_id: UUID, data: CheckoutInput) -> OrderOutput:
        cart = await self._uow.carts.find_by_id(UUID(data.cart_id))
        if cart is None or cart.is_empty():
            raise NotFoundError("Cart not found or empty")

        discount = Money.zero()
        coupon_id = None
        coupon = None
        if data.coupon_code:
            coupon = await self._uow.coupons.find_by_code(data.coupon_code)
            if coupon is None:
                raise NotFoundError("Coupon not found")
            discount = coupon.calculate_discount(cart.subtotal)
            coupon_id = coupon.id

        all_events = []
        for item in cart.items:
            inv = await self._uow.inventory.find_by_sku(str(item.sku))
            if inv is None:
                raise NotFoundError(f"No inventory for SKU {item.sku}")
            inv.reserve(item.quantity)
            await self._uow.inventory.save(inv)
            all_events.extend(inv.collect_events())

        shipping_address = Address.create(
            street=data.shipping_address.street,
            number=data.shipping_address.number,
            complement=data.shipping_address.complement,
            neighborhood=data.shipping_address.neighborhood,
            city=data.shipping_address.city,
            state=data.shipping_address.state,
            cep=data.shipping_address.cep,
            label=data.shipping_address.label,
        )
        order = Order.create_from_cart(
            customer_id=EntityId.from_string(str(customer_id)),
            cart=cart,
            shipping_address=shipping_address,
            shipping_cost=Money.from_decimal(data.shipping_cost),
            discount=discount,
            coupon_id=coupon_id,
        )
        order.mark_awaiting_payment()

        if coupon:
            coupon.redeem()
            await self._uow.coupons.save(coupon)

        await self._uow.orders.save(order)
        cart.clear()
        await self._uow.carts.save(cart)
        all_events.extend(order.collect_events() + cart.collect_events())
        await self._uow.commit()
        await self._event_bus.publish(all_events)
        return _to_order_output(order)


class ProcessPaymentUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, data: CreatePaymentInput, *, customer_email: str) -> PaymentOutput:
        from app.infra.payments.gateways import get_payment_gateway

        gateway = get_payment_gateway(data.provider)
        order = await self._uow.orders.find_by_id(UUID(data.order_id))
        if order is None:
            raise NotFoundError("Order not found")

        payment = Payment.create(
            order_id=order.id,
            amount=order.total,
            method=PaymentMethod(data.method),
            provider=PaymentProvider(data.provider),
        )
        response = await gateway.create_payment(
            PaymentGatewayRequest(
                order_id=order.id.value,
                amount_cents=order.total.amount_cents,
                currency=order.total.currency,
                method=data.method,
                customer_email=customer_email,
                description=f"Order {order.order_number}",
            )
        )
        payment.mark_processing(response.external_id, response.checkout_url)
        if response.status == "approved":
            payment.approve()
            order.mark_paid(payment.id)
            await self._uow.orders.save(order)
        await self._uow.payments.save(payment)
        events = payment.collect_events() + order.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return _to_payment_output(payment)


class UploadProductImageUseCase:
    def __init__(self, storage: StoragePort) -> None:
        self._storage = storage

    async def execute(self, *, product_id: str, filename: str, data: bytes, content_type: str) -> dict:
        key = f"products/{product_id}/{filename}"
        await self._storage.upload(key=key, data=data, content_type=content_type)
        url = await self._storage.get_presigned_url(key=key)
        return {"storage_key": key, "url": url}


class EnrollMfaUseCase:
    def __init__(self, uow: UnitOfWork, mfa: MfaService) -> None:
        self._uow = uow
        self._mfa = mfa
        self._mfa_repo = SqlAlchemyMfaRepository(uow._session)  # noqa: SLF001

    async def execute(self, user_id: UUID) -> MfaEnrollOutput:
        user = await self._uow.users.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        secret = self._mfa.generate_secret()
        await self._mfa_repo.save_secret(user_id, secret, enabled=False)
        await self._uow.commit()
        return MfaEnrollOutput(
            secret=secret,
            provisioning_uri=self._mfa.get_provisioning_uri(secret=secret, email=str(user.email)),
        )


class VerifyMfaUseCase:
    def __init__(self, uow: UnitOfWork, mfa: MfaService) -> None:
        self._uow = uow
        self._mfa = mfa
        self._mfa_repo = SqlAlchemyMfaRepository(uow._session)  # noqa: SLF001

    async def execute(self, user_id: UUID, data: MfaVerifyInput) -> dict:
        secret = await self._mfa_repo.get_secret(user_id)
        if secret is None or not self._mfa.verify_code(secret=secret, code=data.code):
            raise UnauthorizedError("Invalid MFA code")
        await self._mfa_repo.set_enabled(user_id, True)
        user = await self._uow.users.find_by_id(user_id)
        if user:
            user.verify_email()
            user.enable_mfa()
            await self._uow.users.save(user)
        await self._uow.commit()
        return {"mfa_enabled": True}


def _to_coupon_output(coupon: Coupon) -> CouponOutput:
    return CouponOutput(
        id=str(coupon.id.value),
        code=coupon.code,
        discount_type=coupon.discount_type.value,
        discount_value=coupon.discount_value,
        is_active=coupon.is_active,
    )


def _to_payment_output(payment: Payment) -> PaymentOutput:
    return PaymentOutput(
        id=str(payment.id.value),
        order_id=str(payment.order_id.value),
        status=payment.status.value,
        provider=payment.provider.value,
        method=payment.method.value,
        amount=str(payment.amount.to_decimal()),
        checkout_url=payment.checkout_url,
    )
