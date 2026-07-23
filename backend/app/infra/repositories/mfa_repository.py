from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.models.models import UserMfaModel


class SqlAlchemyMfaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_secret(self, user_id: UUID) -> str | None:
        result = await self._session.execute(select(UserMfaModel).where(UserMfaModel.user_id == user_id))
        model = result.scalar_one_or_none()
        return model.secret if model else None

    async def save_secret(self, user_id: UUID, secret: str, *, enabled: bool = False) -> None:
        result = await self._session.execute(select(UserMfaModel).where(UserMfaModel.user_id == user_id))
        model = result.scalar_one_or_none()
        if model is None:
            model = UserMfaModel(user_id=user_id, secret=secret, enabled=enabled)
            self._session.add(model)
        else:
            model.secret = secret
            model.enabled = enabled
        await self._session.flush()

    async def set_enabled(self, user_id: UUID, enabled: bool) -> None:
        result = await self._session.execute(select(UserMfaModel).where(UserMfaModel.user_id == user_id))
        model = result.scalar_one_or_none()
        if model:
            model.enabled = enabled
            await self._session.flush()

    async def is_enabled(self, user_id: UUID) -> bool:
        result = await self._session.execute(select(UserMfaModel).where(UserMfaModel.user_id == user_id))
        model = result.scalar_one_or_none()
        return bool(model and model.enabled)
