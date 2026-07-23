from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from app.domain.shared.exceptions import DomainError

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return normalized.encode("ascii", "ignore").decode("ascii")


@dataclass(frozen=True, slots=True)
class Slug:
    value: str

    @classmethod
    def create(cls, raw: str) -> Slug:
        normalized = _strip_accents(raw.strip().lower())
        normalized = re.sub(r"[^a-z0-9\- ]", "", normalized)
        normalized = re.sub(r"\s+", "-", normalized)
        normalized = re.sub(r"-+", "-", normalized).strip("-")
        if not normalized or not SLUG_PATTERN.match(normalized):
            raise DomainError(f"Invalid slug: {raw}", code="INVALID_SLUG")
        return cls(normalized)

    @classmethod
    def from_name(cls, name: str) -> Slug:
        return cls.create(name)

    def equals(self, other: Slug) -> bool:
        return self.value == other.value

    def __str__(self) -> str:
        return self.value
