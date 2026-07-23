from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.money import Money
from app.domain.shared.value_objects.sku import SKU


@dataclass
class CartItem:
    id: EntityId
    product_id: EntityId
    sku: SKU
    product_name: str
    unit_price: Money
    quantity: int
    added_at: datetime

    @classmethod
    def create(
        cls,
        *,
        product_id: EntityId,
        sku: SKU,
        product_name: str,
        unit_price: Money,
        quantity: int,
    ) -> CartItem:
        if quantity <= 0:
            raise DomainError("Quantity must be greater than zero", code="INVALID_CART")
        return cls(
            id=EntityId.generate(),
            product_id=product_id,
            sku=sku,
            product_name=product_name.strip(),
            unit_price=unit_price,
            quantity=quantity,
            added_at=datetime.now(UTC),
        )

    @classmethod
    def reconstitute(
        cls,
        item_id: EntityId,
        product_id: EntityId,
        sku: SKU,
        product_name: str,
        unit_price: Money,
        quantity: int,
        added_at: datetime,
    ) -> CartItem:
        return cls(
            id=item_id,
            product_id=product_id,
            sku=sku,
            product_name=product_name,
            unit_price=unit_price,
            quantity=quantity,
            added_at=added_at,
        )

    @property
    def line_total(self) -> Money:
        return self.unit_price.multiply(self.quantity)

    def update_quantity(self, quantity: int) -> None:
        if quantity <= 0:
            raise DomainError("Quantity must be greater than zero", code="INVALID_CART")
        self.quantity = quantity
