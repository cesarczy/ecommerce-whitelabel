from __future__ import annotations

from dataclasses import dataclass

from app.domain.shared.exceptions import DomainError


@dataclass(frozen=True, slots=True)
class ProductName:
    value: str

    @classmethod
    def create(cls, raw: str) -> ProductName:
        name = raw.strip()
        if len(name) < 2:
            raise DomainError("Product name must have at least 2 characters", code="INVALID_PRODUCT")
        if len(name) > 200:
            raise DomainError("Product name cannot exceed 200 characters", code="INVALID_PRODUCT")
        return cls(name)

    def equals(self, other: ProductName) -> bool:
        return self.value == other.value

    def __str__(self) -> str:
        return self.value
