from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.commands.auth import LoginUserUseCase, RefreshTokenUseCase, RegisterUserUseCase
from app.application.commands.cart import AddToCartUseCase, GetCartUseCase
from app.application.commands.phase2 import (
    CreateCouponUseCase,
    EnhancedCheckoutUseCase,
    EnrollMfaUseCase,
    ProcessPaymentUseCase,
    UpdateInventoryUseCase,
    UploadProductImageUseCase,
    VerifyMfaUseCase,
)
from app.application.commands.phase3 import (
    CreateReviewUseCase,
    ListCustomerOrdersUseCase,
    ProcessPaymentWebhookUseCase,
    UpdateStoreSettingsUseCase,
)
from app.application.commands.products import CreateProductUseCase, ListProductsUseCase, PublishProductUseCase
from app.application.commands.users import AddUserAddressUseCase, GetUserProfileUseCase
from app.application.queries.dashboard import GetDashboardReportQuery
from app.application.queries.store import (
    GetProductRatingQuery,
    GetStoreSettingsQuery,
    ListBannersQuery,
    ListProductReviewsQuery,
)
from app.core.config.settings import settings
from app.core.database.session import get_session
from app.core.security.jwt import JWTTokenService
from app.core.security.mfa import TotpMfaService
from app.core.security.password import Argon2PasswordHasher
from app.infra.payments.gateways import get_payment_gateway
from app.infra.services.event_bus import CeleryEventBus, InMemoryEventBus
from app.infra.services.unit_of_work import SqlAlchemyUnitOfWork
from app.infra.storage.minio_adapter import InMemoryStorageAdapter, MinIOStorageAdapter

security = HTTPBearer(auto_error=False)
_password_hasher = Argon2PasswordHasher()
_token_service = JWTTokenService()
_mfa_service = TotpMfaService()
_event_bus = CeleryEventBus() if settings.use_celery_events else InMemoryEventBus()

try:
    _storage = MinIOStorageAdapter()
except Exception:
    _storage = InMemoryStorageAdapter()


async def get_uow(session: AsyncSession = Depends(get_session)) -> AsyncGenerator[SqlAlchemyUnitOfWork, None]:
    uow = SqlAlchemyUnitOfWork(session)
    yield uow


def get_register_user(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> RegisterUserUseCase:
    return RegisterUserUseCase(uow, _password_hasher, _event_bus)


def get_login_user(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> LoginUserUseCase:
    return LoginUserUseCase(uow, _password_hasher, _token_service, uow.refresh_tokens)


def get_refresh_token(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(_token_service, uow.refresh_tokens)


def get_user_profile(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> GetUserProfileUseCase:
    return GetUserProfileUseCase(uow)


def get_add_address(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> AddUserAddressUseCase:
    return AddUserAddressUseCase(uow, _event_bus)


def get_create_product(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> CreateProductUseCase:
    return CreateProductUseCase(uow, _event_bus)


def get_publish_product(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> PublishProductUseCase:
    return PublishProductUseCase(uow, _event_bus)


def get_list_products(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> ListProductsUseCase:
    return ListProductsUseCase(uow)


def get_add_to_cart(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> AddToCartUseCase:
    return AddToCartUseCase(uow, _event_bus)


def get_cart(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> GetCartUseCase:
    return GetCartUseCase(uow)


def get_checkout(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> EnhancedCheckoutUseCase:
    return EnhancedCheckoutUseCase(uow, _event_bus)


def get_create_coupon(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> CreateCouponUseCase:
    return CreateCouponUseCase(uow, _event_bus)


def get_update_inventory(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> UpdateInventoryUseCase:
    return UpdateInventoryUseCase(uow, _event_bus)


def get_process_payment(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> ProcessPaymentUseCase:
    return ProcessPaymentUseCase(uow, _event_bus)


def get_upload_image() -> UploadProductImageUseCase:
    return UploadProductImageUseCase(_storage)


def get_enroll_mfa(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> EnrollMfaUseCase:
    return EnrollMfaUseCase(uow, _mfa_service)


def get_verify_mfa(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> VerifyMfaUseCase:
    return VerifyMfaUseCase(uow, _mfa_service)


def get_dashboard_query(session: AsyncSession = Depends(get_session)) -> GetDashboardReportQuery:
    return GetDashboardReportQuery(session)


def get_store_query(session: AsyncSession = Depends(get_session)) -> GetStoreSettingsQuery:
    return GetStoreSettingsQuery(session)


def get_product_reviews_query(session: AsyncSession = Depends(get_session)) -> ListProductReviewsQuery:
    return ListProductReviewsQuery(session)


def get_product_rating_query(session: AsyncSession = Depends(get_session)) -> GetProductRatingQuery:
    return GetProductRatingQuery(session)


def get_banners_query(session: AsyncSession = Depends(get_session)) -> ListBannersQuery:
    return ListBannersQuery(session)


def get_process_webhook(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> ProcessPaymentWebhookUseCase:
    return ProcessPaymentWebhookUseCase(uow, _event_bus)


def get_list_orders(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> ListCustomerOrdersUseCase:
    return ListCustomerOrdersUseCase(uow)


def get_create_review(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> CreateReviewUseCase:
    return CreateReviewUseCase(uow, _event_bus)


def get_update_store(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> UpdateStoreSettingsUseCase:
    return UpdateStoreSettingsUseCase(uow, _event_bus)


async def get_optional_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> UUID | None:
    if credentials is None:
        return None
    try:
        payload = _token_service.verify_access_token(credentials.credentials)
    except ValueError:
        return None
    return UUID(payload["sub"])


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> UUID:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = _token_service.verify_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return UUID(payload["sub"])
