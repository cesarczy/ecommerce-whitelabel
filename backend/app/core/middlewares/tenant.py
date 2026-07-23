from uuid import UUID

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.context.tenant import clear_tenant_context, set_tenant_context

DEFAULT_TENANT_ID = UUID("00000000-0000-4000-8000-000000000010")
DEFAULT_TENANT_SLUG = "default"


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        slug = request.headers.get("X-Tenant-Slug", DEFAULT_TENANT_SLUG)
        tenant_id = getattr(request.state, "tenant_id", None) or DEFAULT_TENANT_ID
        if hasattr(request.app.state, "tenant_resolver"):
            resolved = await request.app.state.tenant_resolver(slug)
            if resolved:
                tenant_id, slug = resolved
        set_tenant_context(tenant_id=tenant_id, slug=slug)
        request.state.tenant_id = tenant_id
        request.state.tenant_slug = slug
        try:
            response = await call_next(request)
        finally:
            clear_tenant_context()
        response.headers["X-Tenant-Slug"] = slug
        return response
