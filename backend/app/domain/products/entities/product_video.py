from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError


@dataclass
class ProductVideo:
    id: EntityId
    product_id: EntityId
    storage_key: str
    title: str
    sort_order: int
    created_at: datetime

    @classmethod
    def create(cls, *, product_id: EntityId, storage_key: str, title: str = "", sort_order: int = 0) -> ProductVideo:
        key = storage_key.strip()
        if not key:
            raise DomainError("Video storage key is required", code="INVALID_VIDEO")
        return cls(
            id=EntityId.generate(),
            product_id=product_id,
            storage_key=key,
            title=title.strip(),
            sort_order=sort_order,
            created_at=datetime.now(UTC),
        )
