import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.ports import EventBus, RefreshTokenStore
from app.domain.shared.domain_event import DomainEvent
from app.infra.models.models import RefreshTokenModel
from app.infra.workers.celery_app import process_domain_event_task

logger = logging.getLogger(__name__)


class InMemoryEventBus(EventBus):
    async def publish(self, events: list[DomainEvent]) -> None:
        for event in events:
            logger.info("domain_event", extra={"event": event.event_name, "aggregate_id": str(event.aggregate_id)})


class CeleryEventBus(EventBus):
    async def publish(self, events: list[DomainEvent]) -> None:
        for event in events:
            payload = {
                k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                for k, v in event.__dict__.items()
                if k != "occurred_at"
            }
            try:
                process_domain_event_task.delay(event.event_name, str(event.aggregate_id), payload)
            except Exception:
                logger.exception("Failed to queue event, falling back to log")
                logger.info("domain_event", extra={"event": event.event_name, "aggregate_id": str(event.aggregate_id)})


class SqlAlchemyRefreshTokenStore(RefreshTokenStore):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def store(self, user_id: UUID, token: str, expires_at: datetime) -> None:
        self._session.add(
            RefreshTokenModel(user_id=user_id, token=token, expires_at=expires_at, revoked=False)
        )
        await self._session.flush()

    async def revoke(self, token: str) -> None:
        result = await self._session.execute(select(RefreshTokenModel).where(RefreshTokenModel.token == token))
        model = result.scalar_one_or_none()
        if model:
            model.revoked = True
            await self._session.flush()

    async def is_valid(self, user_id: UUID, token: str) -> bool:
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.token == token,
                RefreshTokenModel.revoked.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return model is not None and model.expires_at > datetime.now(UTC)
