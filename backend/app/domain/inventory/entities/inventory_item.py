from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.sku import SKU
from app.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True)
class StockLowEvent(DomainEvent):
    sku: str
    available: int
    threshold: int


@dataclass(frozen=True, slots=True, kw_only=True)
class StockReservedEvent(DomainEvent):
    sku: str
    quantity: int


@dataclass
class InventoryItem(AggregateRoot):
    id: EntityId
    product_id: EntityId
    sku: SKU
    quantity_available: int
    quantity_reserved: int
    low_stock_threshold: int
    updated_at: datetime

    def __post_init__(self) -> None:
        super().__init__()

    @classmethod
    def create(
        cls,
        *,
        product_id: EntityId,
        sku: SKU,
        quantity: int,
        low_stock_threshold: int = 5,
    ) -> InventoryItem:
        if quantity < 0:
            raise DomainError("Quantity cannot be negative", code="INVALID_INVENTORY")
        now = datetime.now(UTC)
        return cls(
            id=EntityId.generate(),
            product_id=product_id,
            sku=sku,
            quantity_available=quantity,
            quantity_reserved=0,
            low_stock_threshold=low_stock_threshold,
            updated_at=now,
        )

    @classmethod
    def reconstitute(
        cls,
        *,
        item_id: EntityId,
        product_id: EntityId,
        sku: SKU,
        quantity_available: int,
        quantity_reserved: int,
        low_stock_threshold: int,
        updated_at: datetime,
    ) -> InventoryItem:
        return cls(
            id=item_id,
            product_id=product_id,
            sku=sku,
            quantity_available=quantity_available,
            quantity_reserved=quantity_reserved,
            low_stock_threshold=low_stock_threshold,
            updated_at=updated_at,
        )

    @property
    def total_physical(self) -> int:
        return self.quantity_available + self.quantity_reserved

    def adjust(self, quantity: int) -> None:
        if self.quantity_available + quantity < 0:
            raise DomainError("Insufficient stock for adjustment", code="INSUFFICIENT_STOCK")
        self.quantity_available += quantity
        self.updated_at = datetime.now(UTC)
        self._check_low_stock()

    def reserve(self, quantity: int) -> None:
        if quantity <= 0:
            raise DomainError("Reserve quantity must be positive", code="INVALID_INVENTORY")
        if self.quantity_available < quantity:
            raise DomainError("Insufficient stock", code="INSUFFICIENT_STOCK")
        self.quantity_available -= quantity
        self.quantity_reserved += quantity
        self.updated_at = datetime.now(UTC)
        self._record_event(
            StockReservedEvent(aggregate_id=self.id.value, sku=str(self.sku), quantity=quantity)
        )
        self._check_low_stock()

    def release(self, quantity: int) -> None:
        if quantity <= 0 or self.quantity_reserved < quantity:
            raise DomainError("Invalid release quantity", code="INVALID_INVENTORY")
        self.quantity_reserved -= quantity
        self.quantity_available += quantity
        self.updated_at = datetime.now(UTC)

    def commit_reservation(self, quantity: int) -> None:
        if quantity <= 0 or self.quantity_reserved < quantity:
            raise DomainError("Invalid commit quantity", code="INVALID_INVENTORY")
        self.quantity_reserved -= quantity
        self.updated_at = datetime.now(UTC)
        self._check_low_stock()

    def is_low_stock(self) -> bool:
        return self.quantity_available <= self.low_stock_threshold

    def _check_low_stock(self) -> None:
        if self.is_low_stock():
            self._record_event(
                StockLowEvent(
                    aggregate_id=self.id.value,
                    sku=str(self.sku),
                    available=self.quantity_available,
                    threshold=self.low_stock_threshold,
                )
            )
