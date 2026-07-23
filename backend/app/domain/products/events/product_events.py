from __future__ import annotations

from dataclasses import dataclass

from app.domain.shared.domain_event import DomainEvent
from app.domain.shared.value_objects.money import Money


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductCreatedEvent(DomainEvent):
    name: str
    sku: str
    category_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductPublishedEvent(DomainEvent):
    name: str
    slug: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductPriceChangedEvent(DomainEvent):
    old_price_cents: int
    new_price_cents: int
    currency: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductDeactivatedEvent(DomainEvent):
    reason: str | None = None
