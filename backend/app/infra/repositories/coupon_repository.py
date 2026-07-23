from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.ports import CouponRepository
from app.core.context.tenant import get_current_tenant_id
from app.core.middlewares.tenant import DEFAULT_TENANT_ID
from app.domain.coupon.entities.coupon import Coupon, DiscountType
from app.domain.shared.entity_id import EntityId
from app.infra.models.models import CouponModel


def _tenant_id() -> UUID:
    return get_current_tenant_id() or DEFAULT_TENANT_ID


def _to_domain(model: CouponModel) -> Coupon:
    return Coupon.reconstitute(
        coupon_id=EntityId.from_string(str(model.id)),
        code=model.code,
        discount_type=DiscountType(model.discount_type),
        discount_value=model.discount_value,
        min_order_cents=model.min_order_cents,
        max_uses=model.max_uses,
        used_count=model.used_count,
        valid_from=model.valid_from,
        valid_until=model.valid_until,
        is_active=model.is_active,
        created_at=model.created_at,
    )


class SqlAlchemyCouponRepository(CouponRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, coupon: Coupon) -> None:
        result = await self._session.execute(select(CouponModel).where(CouponModel.id == coupon.id.value))
        model = result.scalar_one_or_none()
        if model is None:
            model = CouponModel(id=coupon.id.value, tenant_id=_tenant_id())
            self._session.add(model)
        model.code = coupon.code
        model.discount_type = coupon.discount_type.value
        model.discount_value = coupon.discount_value
        model.min_order_cents = coupon.min_order_cents
        model.max_uses = coupon.max_uses
        model.used_count = coupon.used_count
        model.valid_from = coupon.valid_from
        model.valid_until = coupon.valid_until
        model.is_active = coupon.is_active
        model.created_at = coupon.created_at
        await self._session.flush()

    async def find_by_code(self, code: str) -> Coupon | None:
        result = await self._session.execute(
            select(CouponModel).where(
                CouponModel.tenant_id == _tenant_id(),
                CouponModel.code == code.strip().upper(),
            )
        )
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def find_by_id(self, coupon_id: UUID) -> Coupon | None:
        result = await self._session.execute(
            select(CouponModel).where(CouponModel.id == coupon_id, CouponModel.tenant_id == _tenant_id())
        )
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def list_active(self) -> list:
        result = await self._session.execute(
            select(CouponModel).where(CouponModel.tenant_id == _tenant_id(), CouponModel.is_active.is_(True))
        )
        return [_to_domain(m) for m in result.scalars().all()]
