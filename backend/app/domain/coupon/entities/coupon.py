from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.money import Money
from app.domain.shared.domain_event import DomainEvent


class DiscountType(StrEnum):
    PERCENT = "percent"
    FIXED = "fixed"


@dataclass(frozen=True, slots=True, kw_only=True)
class CouponCreatedEvent(DomainEvent):
    code: str


@dataclass
class Coupon(AggregateRoot):
    id: EntityId
    code: str
    discount_type: DiscountType
    discount_value: int
    min_order_cents: int
    max_uses: int | None
    used_count: int
    valid_from: datetime
    valid_until: datetime | None
    is_active: bool
    created_at: datetime

    def __post_init__(self) -> None:
        super().__init__()

    @classmethod
    def create(
        cls,
        *,
        code: str,
        discount_type: DiscountType,
        discount_value: int,
        min_order_cents: int = 0,
        max_uses: int | None = None,
        valid_until: datetime | None = None,
    ) -> Coupon:
        normalized = code.strip().upper()
        if len(normalized) < 3:
            raise DomainError("Coupon code must have at least 3 characters", code="INVALID_COUPON")
        if discount_value <= 0:
            raise DomainError("Discount value must be positive", code="INVALID_COUPON")
        if discount_type == DiscountType.PERCENT and discount_value > 100:
            raise DomainError("Percent discount cannot exceed 100", code="INVALID_COUPON")
        now = datetime.now(UTC)
        coupon = cls(
            id=EntityId.generate(),
            code=normalized,
            discount_type=discount_type,
            discount_value=discount_value,
            min_order_cents=min_order_cents,
            max_uses=max_uses,
            used_count=0,
            valid_from=now,
            valid_until=valid_until,
            is_active=True,
            created_at=now,
        )
        coupon._record_event(CouponCreatedEvent(aggregate_id=coupon.id.value, code=normalized))
        return coupon

    @classmethod
    def reconstitute(
        cls,
        *,
        coupon_id: EntityId,
        code: str,
        discount_type: DiscountType,
        discount_value: int,
        min_order_cents: int,
        max_uses: int | None,
        used_count: int,
        valid_from: datetime,
        valid_until: datetime | None,
        is_active: bool,
        created_at: datetime,
    ) -> Coupon:
        return cls(
            id=coupon_id,
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            min_order_cents=min_order_cents,
            max_uses=max_uses,
            used_count=used_count,
            valid_from=valid_from,
            valid_until=valid_until,
            is_active=is_active,
            created_at=created_at,
        )

    def calculate_discount(self, subtotal: Money) -> Money:
        self._ensure_valid(subtotal)
        if self.discount_type == DiscountType.PERCENT:
            cents = (subtotal.amount_cents * self.discount_value) // 100
        else:
            cents = min(self.discount_value, subtotal.amount_cents)
        return Money(cents, subtotal.currency)

    def redeem(self) -> None:
        self._ensure_valid_for_use()
        self.used_count += 1

    def deactivate(self) -> None:
        self.is_active = False

    def _ensure_valid(self, subtotal: Money) -> None:
        self._ensure_valid_for_use()
        if subtotal.amount_cents < self.min_order_cents:
            raise DomainError("Order subtotal below coupon minimum", code="INVALID_COUPON")

    def _ensure_valid_for_use(self) -> None:
        if not self.is_active:
            raise DomainError("Coupon is inactive", code="INVALID_COUPON")
        now = datetime.now(UTC)
        if now < self.valid_from:
            raise DomainError("Coupon not yet valid", code="INVALID_COUPON")
        if self.valid_until and now > self.valid_until:
            raise DomainError("Coupon expired", code="INVALID_COUPON")
        if self.max_uses is not None and self.used_count >= self.max_uses:
            raise DomainError("Coupon usage limit reached", code="INVALID_COUPON")
