from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.shared.exceptions import DomainError

SKU_PATTERN = re.compile(r"^[A-Z0-9\-_.]{3,64}$")


@dataclass(frozen=True, slots=True)
class SKU:
    value: str

    @classmethod
    def create(cls, raw: str) -> SKU:
        normalized = raw.strip().upper()
        if not SKU_PATTERN.match(normalized):
            raise DomainError(f"Invalid SKU: {raw}", code="INVALID_SKU")
        return cls(normalized)

    def equals(self, other: SKU) -> bool:
        return self.value == other.value

    def __str__(self) -> str:
        return self.value
