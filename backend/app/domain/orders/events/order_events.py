from __future__ import annotations

from dataclasses import dataclass

from app.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True)
class CartItemAddedEvent(DomainEvent):
    product_id: str
    sku: str
    quantity: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CartClearedEvent(DomainEvent):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderCreatedEvent(DomainEvent):
    order_number: str
    customer_id: str
    total_cents: int
    currency: str


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderPaidEvent(DomainEvent):
    order_number: str
    payment_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderCancelledEvent(DomainEvent):
    order_number: str
    reason: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class OrderStatusChangedEvent(DomainEvent):
    order_number: str
    old_status: str
    new_status: str
