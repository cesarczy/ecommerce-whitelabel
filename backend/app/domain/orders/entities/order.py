from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.money import Money
from app.domain.orders.entities.cart import Cart
from app.domain.orders.entities.order_item import OrderItem
from app.domain.orders.entities.order_status_history import OrderStatusHistory
from app.domain.orders.enums.order_status import OrderStatus
from app.domain.orders.events.order_events import (
    OrderCancelledEvent,
    OrderCreatedEvent,
    OrderPaidEvent,
    OrderStatusChangedEvent,
)
from app.domain.orders.value_objects.order_number import OrderNumber

TERMINAL_STATUSES = frozenset({OrderStatus.DELIVERED, OrderStatus.CANCELLED})


@dataclass
class Order(AggregateRoot):
    id: EntityId
    order_number: OrderNumber
    customer_id: EntityId
    items: list[OrderItem]
    shipping_address: Address
    status: OrderStatus
    status_history: list[OrderStatusHistory]
    subtotal: Money
    discount: Money
    shipping_cost: Money
    total: Money
    coupon_id: EntityId | None
    payment_id: EntityId | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        super().__init__()
        if not self.items:
            raise DomainError("Order must have at least one item", code="INVALID_ORDER")

    @classmethod
    def create_from_cart(
        cls,
        *,
        customer_id: EntityId,
        cart: Cart,
        shipping_address: Address,
        shipping_cost: Money,
        discount: Money | None = None,
        coupon_id: EntityId | None = None,
    ) -> Order:
        if cart.is_empty():
            raise DomainError("Cannot create order from empty cart", code="INVALID_ORDER")

        items = [
            OrderItem.create(
                product_id=item.product_id,
                sku=item.sku,
                product_name=item.product_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
            )
            for item in cart.items
        ]
        subtotal = cart.subtotal
        discount_amount = discount or Money.zero(subtotal.currency)
        if discount_amount.currency != subtotal.currency:
            raise DomainError("Discount currency mismatch", code="CURRENCY_MISMATCH")
        if discount_amount.amount_cents > subtotal.amount_cents:
            raise DomainError("Discount cannot exceed subtotal", code="INVALID_ORDER")

        total = subtotal.subtract(discount_amount).add(shipping_cost)
        now = datetime.now(UTC)
        order_number = OrderNumber.generate()
        initial_status = OrderStatus.CREATED

        order = cls(
            id=EntityId.generate(),
            order_number=order_number,
            customer_id=customer_id,
            items=items,
            shipping_address=shipping_address,
            status=initial_status,
            status_history=[OrderStatusHistory.create(initial_status)],
            subtotal=subtotal,
            discount=discount_amount,
            shipping_cost=shipping_cost,
            total=total,
            coupon_id=coupon_id,
            payment_id=None,
            created_at=now,
            updated_at=now,
        )
        order._record_event(
            OrderCreatedEvent(
                aggregate_id=order.id.value,
                order_number=str(order_number),
                customer_id=str(customer_id.value),
                total_cents=total.amount_cents,
                currency=total.currency,
            )
        )
        return order

    @classmethod
    def reconstitute(
        cls,
        *,
        order_id: EntityId,
        order_number: OrderNumber,
        customer_id: EntityId,
        items: list[OrderItem],
        shipping_address: Address,
        status: OrderStatus,
        status_history: list[OrderStatusHistory],
        subtotal: Money,
        discount: Money,
        shipping_cost: Money,
        total: Money,
        coupon_id: EntityId | None,
        payment_id: EntityId | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> Order:
        return cls(
            id=order_id,
            order_number=order_number,
            customer_id=customer_id,
            items=items,
            shipping_address=shipping_address,
            status=status,
            status_history=status_history,
            subtotal=subtotal,
            discount=discount,
            shipping_cost=shipping_cost,
            total=total,
            coupon_id=coupon_id,
            payment_id=payment_id,
            created_at=created_at,
            updated_at=updated_at,
        )

    def mark_awaiting_payment(self) -> None:
        self._transition_to(OrderStatus.AWAITING_PAYMENT)

    def mark_paid(self, payment_id: EntityId) -> None:
        if self.status == OrderStatus.PAID:
            return
        self.payment_id = payment_id
        self._transition_to(OrderStatus.PAID)
        self._record_event(
            OrderPaidEvent(
                aggregate_id=self.id.value,
                order_number=str(self.order_number),
                payment_id=str(payment_id.value),
            )
        )

    def mark_processing(self) -> None:
        self._ensure_status(OrderStatus.PAID)
        self._transition_to(OrderStatus.PROCESSING)

    def mark_shipped(self) -> None:
        if self.status not in (OrderStatus.PAID, OrderStatus.PROCESSING):
            raise DomainError("Order must be paid before shipping", code="INVALID_ORDER_TRANSITION")
        self._transition_to(OrderStatus.SHIPPED)

    def mark_delivered(self) -> None:
        self._ensure_status(OrderStatus.SHIPPED)
        self._transition_to(OrderStatus.DELIVERED)

    def cancel(self, reason: str | None = None) -> None:
        if self.status in TERMINAL_STATUSES:
            raise DomainError("Order cannot be cancelled in current status", code="INVALID_ORDER_TRANSITION")
        if self.status == OrderStatus.SHIPPED:
            raise DomainError("Shipped orders cannot be cancelled", code="INVALID_ORDER_TRANSITION")
        self._transition_to(OrderStatus.CANCELLED, note=reason)
        self._record_event(
            OrderCancelledEvent(
                aggregate_id=self.id.value,
                order_number=str(self.order_number),
                reason=reason,
            )
        )

    def _transition_to(self, new_status: OrderStatus, note: str | None = None) -> None:
        if self.status == new_status:
            return
        if self.status in TERMINAL_STATUSES:
            raise DomainError("Order is in terminal status", code="INVALID_ORDER_TRANSITION")
        old_status = self.status
        self.status = new_status
        self.status_history.append(OrderStatusHistory.create(new_status, note=note))
        self.updated_at = datetime.now(UTC)
        self._record_event(
            OrderStatusChangedEvent(
                aggregate_id=self.id.value,
                order_number=str(self.order_number),
                old_status=old_status.value,
                new_status=new_status.value,
            )
        )

    def _ensure_status(self, expected: OrderStatus) -> None:
        if self.status != expected:
            raise DomainError(
                f"Expected status {expected.value}, got {self.status.value}",
                code="INVALID_ORDER_TRANSITION",
            )
