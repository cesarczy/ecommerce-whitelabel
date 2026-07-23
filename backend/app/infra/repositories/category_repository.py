from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_CATEGORY_ID, DEFAULT_CATEGORY_SLUG
from app.infra.models.models import CategoryModel


async def seed_default_category(session: AsyncSession) -> None:
    result = await session.execute(select(CategoryModel).where(CategoryModel.slug == DEFAULT_CATEGORY_SLUG))
    if result.scalar_one_or_none() is None:
        session.add(
            CategoryModel(
                id=DEFAULT_CATEGORY_ID,
                name="Geral",
                slug=DEFAULT_CATEGORY_SLUG,
                parent_id=None,
            )
        )


async def list_categories(session: AsyncSession) -> list[CategoryModel]:
    result = await session.execute(select(CategoryModel).order_by(CategoryModel.name))
    return list(result.scalars().all())
