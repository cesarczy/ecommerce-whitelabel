import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.ports import (
    BannerRepository,
    FavoriteRepository,
    ProductVideoRepository,
    UserTokenRepository,
)
from app.core.context.tenant import get_current_tenant_id
from app.core.middlewares.tenant import DEFAULT_TENANT_ID
from app.domain.catalog.entities.favorite import Favorite
from app.domain.products.entities.product_video import ProductVideo
from app.domain.shared.entity_id import EntityId
from app.domain.store.entities.store_settings import Banner
from app.infra.models.models import BannerModel, FavoriteModel, ProductVideoModel, UserTokenModel


def _tenant_id() -> UUID:
    return get_current_tenant_id() or DEFAULT_TENANT_ID


class SqlAlchemyFavoriteRepository(FavoriteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, favorite: Favorite) -> None:
        model = FavoriteModel(
            id=favorite.id.value,
            tenant_id=_tenant_id(),
            user_id=favorite.user_id.value,
            product_id=favorite.product_id.value,
            created_at=favorite.created_at,
        )
        await self._session.merge(model)
        await self._session.flush()

    async def remove(self, user_id: UUID, product_id: UUID) -> None:
        await self._session.execute(
            delete(FavoriteModel).where(
                FavoriteModel.tenant_id == _tenant_id(),
                FavoriteModel.user_id == user_id,
                FavoriteModel.product_id == product_id,
            )
        )
        await self._session.flush()

    async def list_by_user(self, user_id: UUID) -> list:
        result = await self._session.execute(
            select(FavoriteModel).where(FavoriteModel.tenant_id == _tenant_id(), FavoriteModel.user_id == user_id)
        )
        return [
            Favorite(
                id=EntityId.from_string(str(m.id)),
                user_id=EntityId.from_string(str(m.user_id)),
                product_id=EntityId.from_string(str(m.product_id)),
                created_at=m.created_at,
            )
            for m in result.scalars().all()
        ]

    async def exists(self, user_id: UUID, product_id: UUID) -> bool:
        result = await self._session.execute(
            select(FavoriteModel.id).where(
                FavoriteModel.tenant_id == _tenant_id(),
                FavoriteModel.user_id == user_id,
                FavoriteModel.product_id == product_id,
            )
        )
        return result.scalar_one_or_none() is not None


class SqlAlchemyBannerRepository(BannerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, banner: Banner) -> None:
        result = await self._session.execute(select(BannerModel).where(BannerModel.id == banner.id.value))
        model = result.scalar_one_or_none()
        if model is None:
            model = BannerModel(id=banner.id.value, tenant_id=_tenant_id())
            self._session.add(model)
        model.title = banner.title
        model.image_key = banner.image_key
        model.link_url = banner.link_url
        model.sort_order = banner.sort_order
        model.is_active = banner.is_active
        await self._session.flush()

    async def find_by_id(self, banner_id: UUID):
        result = await self._session.execute(
            select(BannerModel).where(BannerModel.tenant_id == _tenant_id(), BannerModel.id == banner_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return Banner(
            id=EntityId.from_string(str(model.id)),
            title=model.title,
            image_key=model.image_key,
            link_url=model.link_url,
            sort_order=model.sort_order,
            is_active=model.is_active,
        )

    async def delete(self, banner_id: UUID) -> None:
        await self._session.execute(
            delete(BannerModel).where(BannerModel.tenant_id == _tenant_id(), BannerModel.id == banner_id)
        )
        await self._session.flush()

    async def list_active(self, tenant_id: UUID) -> list:
        result = await self._session.execute(
            select(BannerModel)
            .where(BannerModel.tenant_id == tenant_id, BannerModel.is_active.is_(True))
            .order_by(BannerModel.sort_order)
        )
        return [
            Banner(
                id=EntityId.from_string(str(m.id)),
                title=m.title,
                image_key=m.image_key,
                link_url=m.link_url,
                sort_order=m.sort_order,
                is_active=m.is_active,
            )
            for m in result.scalars().all()
        ]


class SqlAlchemyUserTokenRepository(UserTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, user_id: UUID, token: str, token_type: str, expires_at: datetime) -> None:
        self._session.add(
            UserTokenModel(user_id=user_id, token=token, token_type=token_type, expires_at=expires_at, used=False)
        )
        await self._session.flush()

    async def find_user_by_token(self, token: str, token_type: str):
        result = await self._session.execute(
            select(UserTokenModel).where(
                UserTokenModel.token == token,
                UserTokenModel.token_type == token_type,
                UserTokenModel.used.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        if model is None or model.expires_at < datetime.now(UTC):
            return None
        return model.user_id

    async def invalidate(self, token: str) -> None:
        result = await self._session.execute(select(UserTokenModel).where(UserTokenModel.token == token))
        model = result.scalar_one_or_none()
        if model:
            model.used = True
            await self._session.flush()


class SqlAlchemyProductVideoRepository(ProductVideoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, video: ProductVideo) -> None:
        model = ProductVideoModel(
            id=video.id.value,
            product_id=video.product_id.value,
            storage_key=video.storage_key,
            title=video.title,
            sort_order=video.sort_order,
            created_at=video.created_at,
        )
        await self._session.merge(model)
        await self._session.flush()

    async def list_by_product(self, product_id: UUID) -> list:
        result = await self._session.execute(
            select(ProductVideoModel)
            .where(ProductVideoModel.product_id == product_id)
            .order_by(ProductVideoModel.sort_order)
        )
        return [
            ProductVideo(
                id=EntityId.from_string(str(m.id)),
                product_id=EntityId.from_string(str(m.product_id)),
                storage_key=m.storage_key,
                title=m.title,
                sort_order=m.sort_order,
                created_at=m.created_at,
            )
            for m in result.scalars().all()
        ]


def generate_secure_token() -> str:
    return secrets.token_urlsafe(32)


def token_expiry(hours: int = 24) -> datetime:
    return datetime.now(UTC) + timedelta(hours=hours)
