from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError


@dataclass
class ProductImage:
    id: EntityId
    storage_key: str
    alt_text: str
    sort_order: int
    is_primary: bool
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        storage_key: str,
        alt_text: str = "",
        sort_order: int = 0,
        is_primary: bool = False,
    ) -> ProductImage:
        key = storage_key.strip()
        if not key:
            raise DomainError("Image storage key is required", code="INVALID_PRODUCT")
        return cls(
            id=EntityId.generate(),
            storage_key=key,
            alt_text=alt_text.strip(),
            sort_order=sort_order,
            is_primary=is_primary,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def reconstitute(
        cls,
        image_id: EntityId,
        storage_key: str,
        alt_text: str,
        sort_order: int,
        is_primary: bool,
        created_at: datetime,
    ) -> ProductImage:
        return cls(
            id=image_id,
            storage_key=storage_key,
            alt_text=alt_text,
            sort_order=sort_order,
            is_primary=is_primary,
            created_at=created_at,
        )
