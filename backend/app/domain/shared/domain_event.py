from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent(ABC):
    aggregate_id: UUID
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def event_name(self) -> str:
        return self.__class__.__name__
