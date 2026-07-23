from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.ports import ReviewRepository, StoreRepository
from app.core.context.tenant import get_current_tenant_id
from app.core.middlewares.tenant import DEFAULT_TENANT_ID
from app.domain.review.entities.review import Review
from app.domain.shared.entity_id import EntityId
from app.domain.store.entities.store_settings import StoreSettings
from app.infra.models.models import ReviewModel, StoreSettingsModel


def _tenant_id() -> UUID:
    return get_current_tenant_id() or DEFAULT_TENANT_ID


class SqlAlchemyReviewRepository(ReviewRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, review: Review) -> None:
        model = ReviewModel(
            id=review.id.value,
            tenant_id=_tenant_id(),
            product_id=review.product_id.value,
            customer_id=review.customer_id.value,
            order_id=review.order_id.value if review.order_id else None,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            created_at=review.created_at,
        )
        await self._session.merge(model)
        await self._session.flush()

    async def find_by_product_id(self, product_id: UUID) -> list:
        result = await self._session.execute(
            select(ReviewModel).where(
                ReviewModel.tenant_id == _tenant_id(),
                ReviewModel.product_id == product_id,
            )
        )
        return [
            Review.reconstitute(
                review_id=EntityId.from_string(str(m.id)),
                product_id=EntityId.from_string(str(m.product_id)),
                customer_id=EntityId.from_string(str(m.customer_id)),
                order_id=EntityId.from_string(str(m.order_id)) if m.order_id else None,
                rating=m.rating,
                title=m.title,
                comment=m.comment,
                created_at=m.created_at,
            )
            for m in result.scalars().all()
        ]


class SqlAlchemyStoreRepository(StoreRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, store: StoreSettings) -> None:
        result = await self._session.execute(
            select(StoreSettingsModel).where(StoreSettingsModel.tenant_id == store.tenant_id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            model = StoreSettingsModel(id=store.id.value, tenant_id=store.tenant_id.value)
            self._session.add(model)
        model.name = store.name
        model.tagline = store.tagline
        model.logo_url = store.logo_url
        model.primary_color = store.primary_color
        model.secondary_color = store.secondary_color
        model.support_email = store.support_email
        model.updated_at = store.updated_at
        await self._session.flush()

    async def find_by_tenant_id(self, tenant_id: UUID) -> StoreSettings | None:
        result = await self._session.execute(
            select(StoreSettingsModel).where(StoreSettingsModel.tenant_id == tenant_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return StoreSettings.reconstitute(
            store_id=EntityId.from_string(str(model.id)),
            tenant_id=EntityId.from_string(str(model.tenant_id)),
            name=model.name,
            tagline=model.tagline,
            logo_url=model.logo_url,
            primary_color=model.primary_color,
            secondary_color=model.secondary_color,
            support_email=model.support_email,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
