from contextvars import ContextVar
from uuid import UUID

_tenant_id: ContextVar[UUID | None] = ContextVar("tenant_id", default=None)
_tenant_slug: ContextVar[str | None] = ContextVar("tenant_slug", default=None)


def set_tenant_context(*, tenant_id: UUID, slug: str) -> None:
    _tenant_id.set(tenant_id)
    _tenant_slug.set(slug)


def get_current_tenant_id() -> UUID | None:
    return _tenant_id.get()


def get_current_tenant_slug() -> str | None:
    return _tenant_slug.get()


def clear_tenant_context() -> None:
    _tenant_id.set(None)
    _tenant_slug.set(None)
