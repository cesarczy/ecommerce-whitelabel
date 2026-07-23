from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.commands.auth import LoginUserUseCase, RefreshTokenUseCase, RegisterUserUseCase
from app.application.commands.cart import AddToCartUseCase, CheckoutUseCase, GetCartUseCase
from app.application.commands.products import CreateProductUseCase, ListProductsUseCase, PublishProductUseCase
from app.application.commands.users import AddUserAddressUseCase, GetUserProfileUseCase
from app.core.database.session import get_session
from app.core.security.jwt import JWTTokenService
from app.core.security.password import Argon2PasswordHasher
from app.infra.services.event_bus import InMemoryEventBus, SqlAlchemyRefreshTokenStore
from app.infra.services.unit_of_work import SqlAlchemyUnitOfWork

security = HTTPBearer(auto_error=False)
_password_hasher = Argon2PasswordHasher()
_token_service = JWTTokenService()
_event_bus = InMemoryEventBus()


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


def get_checkout(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> CheckoutUseCase:
    return CheckoutUseCase(uow, _event_bus)


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
