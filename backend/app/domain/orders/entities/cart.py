from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.money import Money
from app.domain.shared.value_objects.sku import SKU
from app.domain.orders.entities.cart_item import CartItem
from app.domain.orders.events.order_events import CartClearedEvent, CartItemAddedEvent


@dataclass
class Cart(AggregateRoot):
    id: EntityId
    customer_id: EntityId | None
    session_id: str | None
    items: list[CartItem]
    coupon_code: str | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        super().__init__()
        if self.customer_id is None and self.session_id is None:
            raise DomainError("Cart requires customer_id or session_id", code="INVALID_CART")

    @classmethod
    def create(
        cls,
        *,
        customer_id: EntityId | None = None,
        session_id: str | None = None,
    ) -> Cart:
        if customer_id is None and session_id is None:
            raise DomainError("Cart requires customer_id or session_id", code="INVALID_CART")
        now = datetime.now(UTC)
        return cls(
            id=EntityId.generate(),
            customer_id=customer_id,
            session_id=session_id.strip() if session_id else None,
            items=[],
            coupon_code=None,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def reconstitute(
        cls,
        *,
        cart_id: EntityId,
        customer_id: EntityId | None,
        session_id: str | None,
        items: list[CartItem],
        coupon_code: str | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> Cart:
        return cls(
            id=cart_id,
            customer_id=customer_id,
            session_id=session_id,
            items=items,
            coupon_code=coupon_code,
            created_at=created_at,
            updated_at=updated_at,
        )

    def add_item(
        self,
        *,
        product_id: EntityId,
        sku: SKU,
        product_name: str,
        unit_price: Money,
        quantity: int,
    ) -> CartItem:
        for item in self.items:
            if item.product_id.value == product_id.value and item.sku.value == sku.value:
                item.update_quantity(item.quantity + quantity)
                self.updated_at = datetime.now(UTC)
                return item

        item = CartItem.create(
            product_id=product_id,
            sku=sku,
            product_name=product_name,
            unit_price=unit_price,
            quantity=quantity,
        )
        self.items.append(item)
        self.updated_at = datetime.now(UTC)
        self._record_event(
            CartItemAddedEvent(
                aggregate_id=self.id.value,
                product_id=str(product_id.value),
                sku=str(sku),
                quantity=quantity,
            )
        )
        return item

    def update_item_quantity(self, item_id: EntityId, quantity: int) -> None:
        item = self._find_item(item_id)
        item.update_quantity(quantity)
        self.updated_at = datetime.now(UTC)

    def remove_item(self, item_id: EntityId) -> None:
        before = len(self.items)
        self.items = [item for item in self.items if item.id.value != item_id.value]
        if len(self.items) == before:
            raise DomainError("Cart item not found", code="CART_ITEM_NOT_FOUND")
        self.updated_at = datetime.now(UTC)

    def apply_coupon(self, coupon_code: str) -> None:
        code = coupon_code.strip().upper()
        if not code:
            raise DomainError("Coupon code cannot be empty", code="INVALID_COUPON")
        self.coupon_code = code
        self.updated_at = datetime.now(UTC)

    def remove_coupon(self) -> None:
        self.coupon_code = None
        self.updated_at = datetime.now(UTC)

    def clear(self) -> None:
        if not self.items:
            return
        self.items.clear()
        self.coupon_code = None
        self.updated_at = datetime.now(UTC)
        self._record_event(CartClearedEvent(aggregate_id=self.id.value))

    @property
    def subtotal(self) -> Money:
        if not self.items:
            return Money.zero()
        total = self.items[0].line_total
        for item in self.items[1:]:
            total = total.add(item.line_total)
        return total

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def _find_item(self, item_id: EntityId) -> CartItem:
        for item in self.items:
            if item.id.value == item_id.value:
                return item
        raise DomainError("Cart item not found", code="CART_ITEM_NOT_FOUND")
