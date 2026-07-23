from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.orders.enums.order_status import OrderStatus


@dataclass
class OrderStatusHistory:
    status: OrderStatus
    changed_at: datetime
    note: str | None = None

    @classmethod
    def create(cls, status: OrderStatus, note: str | None = None) -> OrderStatusHistory:
        return cls(status=status, changed_at=datetime.now(UTC), note=note)

    @classmethod
    def reconstitute(
        cls,
        status: OrderStatus,
        changed_at: datetime,
        note: str | None,
    ) -> OrderStatusHistory:
        return cls(status=status, changed_at=changed_at, note=note)
