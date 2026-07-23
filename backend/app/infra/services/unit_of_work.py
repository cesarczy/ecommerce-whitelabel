from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.ports import UnitOfWork
from app.infra.repositories.coupon_repository import SqlAlchemyCouponRepository
from app.infra.repositories.inventory_repository import SqlAlchemyInventoryRepository
from app.infra.repositories.order_repository import SqlAlchemyCartRepository, SqlAlchemyOrderRepository
from app.infra.repositories.payment_repository import SqlAlchemyPaymentRepository
from app.infra.repositories.product_repository import SqlAlchemyProductRepository
from app.infra.repositories.phase4_repositories import (
    SqlAlchemyBannerRepository,
    SqlAlchemyFavoriteRepository,
    SqlAlchemyProductVideoRepository,
    SqlAlchemyUserTokenRepository,
)
from app.infra.repositories.phase3_repositories import SqlAlchemyReviewRepository, SqlAlchemyStoreRepository
from app.infra.repositories.tenant_repository import SqlAlchemyTenantRepository
from app.infra.repositories.user_repository import SqlAlchemyUserRepository
from app.infra.services.event_bus import SqlAlchemyRefreshTokenStore


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.users = SqlAlchemyUserRepository(session)
        self.products = SqlAlchemyProductRepository(session)
        self.carts = SqlAlchemyCartRepository(session)
        self.orders = SqlAlchemyOrderRepository(session)
        self.payments = SqlAlchemyPaymentRepository(session)
        self.coupons = SqlAlchemyCouponRepository(session)
        self.inventory = SqlAlchemyInventoryRepository(session)
        self.tenants = SqlAlchemyTenantRepository(session)
        self.reviews = SqlAlchemyReviewRepository(session)
        self.stores = SqlAlchemyStoreRepository(session)
        self.favorites = SqlAlchemyFavoriteRepository(session)
        self.banners = SqlAlchemyBannerRepository(session)
        self.user_tokens = SqlAlchemyUserTokenRepository(session)
        self.product_videos = SqlAlchemyProductVideoRepository(session)
        self.refresh_tokens = SqlAlchemyRefreshTokenStore(session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type:
            await self.rollback()
