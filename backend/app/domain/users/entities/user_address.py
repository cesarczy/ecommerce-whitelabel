from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.entity_id import EntityId
from app.domain.shared.value_objects.address import Address


@dataclass
class UserAddress:
    id: EntityId
    address: Address
    is_default: bool
    created_at: datetime

    @classmethod
    def create(cls, address: Address, *, is_default: bool = False) -> UserAddress:
        return cls(
            id=EntityId.generate(),
            address=address,
            is_default=is_default,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def reconstitute(
        cls,
        address_id: EntityId,
        address: Address,
        is_default: bool,
        created_at: datetime,
    ) -> UserAddress:
        return cls(id=address_id, address=address, is_default=is_default, created_at=created_at)
