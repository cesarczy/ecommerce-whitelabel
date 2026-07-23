from uuid import UUID

from app.application.dto.schemas import RegisterUserInput, TokenOutput, UserOutput
from app.application.exceptions import ConflictError
from app.application.interfaces.ports import EventBus, PasswordHasher, UnitOfWork
from app.domain.users.entities.user import User


class RegisterUserUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: PasswordHasher,
        event_bus: EventBus,
    ) -> None:
        self._uow = uow
        self._password_hasher = password_hasher
        self._event_bus = event_bus

    async def execute(self, data: RegisterUserInput) -> UserOutput:
        if await self._uow.users.exists_by_email(str(data.email)):
            raise ConflictError("Email already registered")

        user = User.create(
            email=str(data.email),
            full_name=data.full_name,
            password_hash=self._password_hasher.hash(data.password),
            phone=data.phone,
        )
        await self._uow.users.save(user)
        events = user.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return _to_user_output(user)


class LoginUserUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: PasswordHasher,
        token_service,
        refresh_token_store,
    ) -> None:
        self._uow = uow
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._refresh_token_store = refresh_token_store

    async def execute(self, email: str, password: str) -> TokenOutput:
        from app.application.exceptions import UnauthorizedError

        user = await self._uow.users.find_by_email(email)
        if user is None or not self._password_hasher.verify(password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")

        roles = [role.name for role in user.roles]
        tokens = self._token_service.create_tokens(user.id.value, roles)
        from datetime import UTC, datetime, timedelta

        await self._refresh_token_store.store(
            user.id.value,
            tokens.refresh_token,
            datetime.now(UTC) + timedelta(days=7),
        )
        return TokenOutput(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.expires_in,
        )


class RefreshTokenUseCase:
    def __init__(self, token_service, refresh_token_store) -> None:
        self._token_service = token_service
        self._refresh_token_store = refresh_token_store

    async def execute(self, refresh_token: str) -> TokenOutput:
        from app.application.exceptions import UnauthorizedError

        payload = self._token_service.verify_refresh_token(refresh_token)
        user_id = UUID(payload["sub"])
        if not await self._refresh_token_store.is_valid(user_id, refresh_token):
            raise UnauthorizedError("Invalid refresh token")

        await self._refresh_token_store.revoke(refresh_token)
        tokens = self._token_service.rotate_refresh_token(refresh_token)
        from datetime import UTC, datetime, timedelta

        await self._refresh_token_store.store(
            user_id,
            tokens.refresh_token,
            datetime.now(UTC) + timedelta(days=7),
        )
        return TokenOutput(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.expires_in,
        )


def _to_user_output(user: User) -> UserOutput:
    return UserOutput(
        id=str(user.id.value),
        email=str(user.email),
        full_name=user.full_name,
        phone=str(user.phone) if user.phone else None,
        email_verified=user.email_verified,
        roles=[role.name for role in user.roles],
    )
