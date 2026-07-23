from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.exceptions import DomainError


ORDER_NUMBER_PATTERN = re.compile(r"^ORD-\d{8}-\d{6}$")


@dataclass(frozen=True, slots=True)
class OrderNumber:
    value: str

    @classmethod
    def generate(cls) -> OrderNumber:
        now = datetime.now(UTC)
        return cls(f"ORD-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}")

    @classmethod
    def create(cls, raw: str) -> OrderNumber:
        normalized = raw.strip().upper()
        if not ORDER_NUMBER_PATTERN.match(normalized):
            raise DomainError(f"Invalid order number: {raw}", code="INVALID_ORDER")
        return cls(normalized)

    def __str__(self) -> str:
        return self.value
