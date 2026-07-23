from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.shared.exceptions import DomainError

CEP_PATTERN = re.compile(r"^\d{8}$")


@dataclass(frozen=True, slots=True)
class CEP:
    value: str

    @classmethod
    def create(cls, raw: str) -> CEP:
        digits = re.sub(r"\D", "", raw)
        if not CEP_PATTERN.match(digits):
            raise DomainError(f"Invalid CEP: {raw}", code="INVALID_CEP")
        return cls(digits)

    @property
    def formatted(self) -> str:
        return f"{self.value[:5]}-{self.value[5:]}"

    def equals(self, other: CEP) -> bool:
        return self.value == other.value

    def __str__(self) -> str:
        return self.formatted
