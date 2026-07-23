from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.ports import InventoryRepository
from app.core.context.tenant import get_current_tenant_id
from app.core.middlewares.tenant import DEFAULT_TENANT_ID
from app.domain.inventory.entities.inventory_item import InventoryItem
from app.domain.shared.entity_id import EntityId
from app.domain.shared.value_objects.sku import SKU
from app.infra.models.models import InventoryModel


def _tenant_id() -> UUID:
    return get_current_tenant_id() or DEFAULT_TENANT_ID


def _to_domain(model: InventoryModel) -> InventoryItem:
    return InventoryItem.reconstitute(
        item_id=EntityId.from_string(str(model.id)),
        product_id=EntityId.from_string(str(model.product_id)),
        sku=SKU.create(model.sku),
        quantity_available=model.quantity_available,
        quantity_reserved=model.quantity_reserved,
        low_stock_threshold=model.low_stock_threshold,
        updated_at=model.updated_at,
    )


class SqlAlchemyInventoryRepository(InventoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, item: InventoryItem) -> None:
        result = await self._session.execute(select(InventoryModel).where(InventoryModel.id == item.id.value))
        model = result.scalar_one_or_none()
        if model is None:
            model = InventoryModel(id=item.id.value, tenant_id=_tenant_id(), product_id=item.product_id.value)
            self._session.add(model)
        model.sku = str(item.sku)
        model.quantity_available = item.quantity_available
        model.quantity_reserved = item.quantity_reserved
        model.low_stock_threshold = item.low_stock_threshold
        model.updated_at = item.updated_at
        await self._session.flush()

    async def find_by_sku(self, sku: str) -> InventoryItem | None:
        normalized = sku.strip().upper()
        result = await self._session.execute(
            select(InventoryModel).where(InventoryModel.tenant_id == _tenant_id(), InventoryModel.sku == normalized)
        )
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def find_low_stock(self) -> list:
        result = await self._session.execute(
            select(InventoryModel).where(
                InventoryModel.tenant_id == _tenant_id(),
                InventoryModel.quantity_available <= InventoryModel.low_stock_threshold,
            )
        )
        return [_to_domain(m) for m in result.scalars().all()]
