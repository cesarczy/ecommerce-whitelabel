from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from app.domain.shared.exceptions import DomainError


@dataclass(frozen=True, slots=True)
class EntityId:
    value: UUID

    @classmethod
    def generate(cls) -> EntityId:
        return cls(uuid4())

    @classmethod
    def from_string(cls, raw: str) -> EntityId:
        try:
            return cls(UUID(raw))
        except (ValueError, TypeError) as exc:
            raise DomainError(f"Invalid entity id: {raw}", code="INVALID_ENTITY_ID") from exc

    def __str__(self) -> str:
        return str(self.value)
