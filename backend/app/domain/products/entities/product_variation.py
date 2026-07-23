from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.money import Money
from app.domain.shared.value_objects.sku import SKU


@dataclass
class ProductVariation:
    id: EntityId
    sku: SKU
    attributes: dict[str, str]
    price: Money
    barcode: str | None
    is_active: bool
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        sku: str | SKU,
        attributes: dict[str, str],
        price: Money,
        barcode: str | None = None,
    ) -> ProductVariation:
        sku_vo = sku if isinstance(sku, SKU) else SKU.create(sku)
        if not attributes:
            raise DomainError("Variation must have at least one attribute", code="INVALID_PRODUCT")
        normalized_attrs = {k.strip().lower(): v.strip() for k, v in attributes.items()}
        if any(not k or not v for k, v in normalized_attrs.items()):
            raise DomainError("Variation attributes cannot be empty", code="INVALID_PRODUCT")
        return cls(
            id=EntityId.generate(),
            sku=sku_vo,
            attributes=normalized_attrs,
            price=price,
            barcode=barcode.strip() if barcode else None,
            is_active=True,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def reconstitute(
        cls,
        variation_id: EntityId,
        sku: SKU,
        attributes: dict[str, str],
        price: Money,
        barcode: str | None,
        is_active: bool,
        created_at: datetime,
    ) -> ProductVariation:
        return cls(
            id=variation_id,
            sku=sku,
            attributes=attributes,
            price=price,
            barcode=barcode,
            is_active=is_active,
            created_at=created_at,
        )

    def deactivate(self) -> None:
        self.is_active = False
