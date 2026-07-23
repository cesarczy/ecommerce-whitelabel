from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security.jwt import JWTTokenService

_security = HTTPBearer(auto_error=False)
_token_service = JWTTokenService()

ADMIN_ROLES = frozenset({"admin"})
STAFF_ROLES = frozenset({"admin", "staff"})


def _extract_payload(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        return _token_service.verify_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_security)],
) -> dict:
    return _extract_payload(credentials)


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_security)],
) -> UUID:
    payload = _extract_payload(credentials)
    return UUID(payload["sub"])


async def get_optional_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_security)],
) -> UUID | None:
    if credentials is None:
        return None
    try:
        payload = _token_service.verify_access_token(credentials.credentials)
    except ValueError:
        return None
    return UUID(payload["sub"])


def require_roles(*allowed_roles: str) -> Callable:
    allowed = frozenset(allowed_roles)

    async def _dependency(payload: dict = Depends(get_token_payload)) -> dict:
        user_roles = set(payload.get("roles", []))
        if not user_roles.intersection(allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return payload

    return _dependency


require_admin = require_roles("admin")
require_staff = require_roles("admin", "staff")
