from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.schemas import BannerOutput, StoreSettingsOutput
from app.core.context.tenant import get_current_tenant_id
from app.core.middlewares.tenant import DEFAULT_TENANT_ID
from app.infra.models.models import BannerModel, ReviewModel, StoreSettingsModel


class GetStoreSettingsQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self) -> StoreSettingsOutput:
        tenant_id = get_current_tenant_id() or DEFAULT_TENANT_ID
        result = await self._session.execute(
            select(StoreSettingsModel).where(StoreSettingsModel.tenant_id == tenant_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return StoreSettingsOutput(
                name="Whitelabel Store",
                tagline="",
                logo_url=None,
                primary_color="#4F46E5",
                secondary_color="#6366F1",
            )
        return StoreSettingsOutput(
            name=model.name,
            tagline=model.tagline,
            logo_url=model.logo_url,
            primary_color=model.primary_color,
            secondary_color=model.secondary_color,
        )


class ListBannersQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self) -> list[BannerOutput]:
        tenant_id = get_current_tenant_id() or DEFAULT_TENANT_ID
        result = await self._session.execute(
            select(BannerModel)
            .where(BannerModel.tenant_id == tenant_id, BannerModel.is_active.is_(True))
            .order_by(BannerModel.sort_order)
        )
        return [
            BannerOutput(
                id=str(b.id),
                title=b.title,
                image_url=b.image_key,
                link_url=b.link_url,
                sort_order=b.sort_order,
            )
            for b in result.scalars().all()
        ]


class ListProductReviewsQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self, product_id: UUID) -> list[dict]:
        tenant_id = get_current_tenant_id() or DEFAULT_TENANT_ID
        result = await self._session.execute(
            select(ReviewModel)
            .where(ReviewModel.tenant_id == tenant_id, ReviewModel.product_id == product_id)
            .order_by(ReviewModel.created_at.desc())
        )
        return [
            {
                "id": str(r.id),
                "product_id": str(r.product_id),
                "rating": r.rating,
                "title": r.title,
                "comment": r.comment,
            }
            for r in result.scalars().all()
        ]


class GetProductRatingQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self, product_id: UUID) -> dict:
        from sqlalchemy import func

        tenant_id = get_current_tenant_id() or DEFAULT_TENANT_ID
        result = await self._session.execute(
            select(func.avg(ReviewModel.rating), func.count(ReviewModel.id)).where(
                ReviewModel.tenant_id == tenant_id,
                ReviewModel.product_id == product_id,
            )
        )
        avg_rating, count = result.one()
        return {
            "product_id": str(product_id),
            "average_rating": round(float(avg_rating or 0), 2),
            "review_count": int(count or 0),
        }
