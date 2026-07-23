from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.ports import TenantRepository
from app.core.context.tenant import get_current_tenant_id
from app.domain.store.entities.tenant import Tenant
from app.domain.shared.entity_id import EntityId
from app.infra.models.models import TenantModel


def _to_domain(model: TenantModel) -> Tenant:
    return Tenant.reconstitute(
        tenant_id=EntityId.from_string(str(model.id)),
        slug=model.slug,
        name=model.name,
        domain=model.domain,
        is_active=model.is_active,
        created_at=model.created_at,
    )


class SqlAlchemyTenantRepository(TenantRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, tenant: Tenant) -> None:
        result = await self._session.execute(select(TenantModel).where(TenantModel.id == tenant.id.value))
        model = result.scalar_one_or_none()
        if model is None:
            model = TenantModel(id=tenant.id.value)
            self._session.add(model)
        model.slug = tenant.slug
        model.name = tenant.name
        model.domain = tenant.domain
        model.is_active = tenant.is_active
        model.created_at = tenant.created_at
        await self._session.flush()

    async def find_by_slug(self, slug: str) -> Tenant | None:
        result = await self._session.execute(select(TenantModel).where(TenantModel.slug == slug.lower()))
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def find_by_id(self, tenant_id: UUID) -> Tenant | None:
        result = await self._session.execute(select(TenantModel).where(TenantModel.id == tenant_id))
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None


async def seed_default_tenant(session: AsyncSession) -> None:
    from app.core.middlewares.tenant import DEFAULT_TENANT_ID, DEFAULT_TENANT_SLUG

    result = await session.execute(select(TenantModel).where(TenantModel.slug == DEFAULT_TENANT_SLUG))
    if result.scalar_one_or_none() is None:
        session.add(
            TenantModel(
                id=DEFAULT_TENANT_ID,
                slug=DEFAULT_TENANT_SLUG,
                name="Default Store",
                domain=None,
                is_active=True,
            )
        )
