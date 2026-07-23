from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.shared.exceptions import DomainError

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    @classmethod
    def create(cls, raw: str) -> Email:
        normalized = raw.strip().lower()
        if not normalized or not EMAIL_PATTERN.match(normalized):
            raise DomainError(f"Invalid email: {raw}", code="INVALID_EMAIL")
        return cls(normalized)

    def equals(self, other: Email) -> bool:
        return self.value == other.value

    def __str__(self) -> str:
        return self.value
