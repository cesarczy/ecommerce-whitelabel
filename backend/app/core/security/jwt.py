from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from app.application.interfaces.ports import TokenPair, TokenService
from app.core.config.settings import settings


class JWTTokenService(TokenService):
    def __init__(self) -> None:
        self._algorithm = "HS256"
        self._secret = settings.secret_key

    def create_tokens(self, user_id: UUID, roles: list[str]) -> TokenPair:
        access = self._create_token(
            user_id,
            roles,
            timedelta(minutes=settings.jwt_access_token_expire_minutes),
            token_type="access",
        )
        refresh = self._create_token(
            user_id,
            roles,
            timedelta(days=settings.jwt_refresh_token_expire_days),
            token_type="refresh",
        )
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    def verify_access_token(self, token: str) -> dict:
        return self._verify(token, expected_type="access")

    def verify_refresh_token(self, token: str) -> dict:
        return self._verify(token, expected_type="refresh")

    def rotate_refresh_token(self, refresh_token: str) -> TokenPair:
        payload = self.verify_refresh_token(refresh_token)
        return self.create_tokens(UUID(payload["sub"]), payload.get("roles", []))

    def _create_token(
        self,
        user_id: UUID,
        roles: list[str],
        expires_delta: timedelta,
        *,
        token_type: str,
    ) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "roles": roles,
            "type": token_type,
            "iat": now,
            "exp": now + expires_delta,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def _verify(self, token: str, *, expected_type: str) -> dict:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError as exc:
            raise ValueError("Invalid token") from exc
        if payload.get("type") != expected_type:
            raise ValueError("Invalid token type")
        return payload
