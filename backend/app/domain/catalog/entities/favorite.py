from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.entity_id import EntityId


@dataclass
class Favorite:
    id: EntityId
    user_id: EntityId
    product_id: EntityId
    created_at: datetime

    @classmethod
    def create(cls, *, user_id: EntityId, product_id: EntityId) -> Favorite:
        return cls(
            id=EntityId.generate(),
            user_id=user_id,
            product_id=product_id,
            created_at=datetime.now(UTC),
        )
