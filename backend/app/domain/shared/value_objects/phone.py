from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.shared.exceptions import DomainError

PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{9,14}$")


@dataclass(frozen=True, slots=True)
class Phone:
    value: str

    @classmethod
    def create(cls, raw: str) -> Phone:
        digits = re.sub(r"\D", "", raw)
        if not PHONE_PATTERN.match(digits):
            raise DomainError(f"Invalid phone: {raw}", code="INVALID_PHONE")
        return cls(digits)

    def equals(self, other: Phone) -> bool:
        return self.value == other.value

    def __str__(self) -> str:
        return self.value
