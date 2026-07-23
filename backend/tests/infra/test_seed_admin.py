import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.domain.users.entities.role import ADMIN_ROLE
from app.infra.repositories.user_repository import seed_default_admin


@pytest.mark.asyncio
async def test_seed_default_admin_creates_user_when_missing() -> None:
    session = AsyncMock()
    empty_result = MagicMock()
    empty_result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=empty_result)

    with patch("app.infra.repositories.user_repository.SqlAlchemyUserRepository") as repo_cls:
        repo = AsyncMock()
        repo_cls.return_value = repo
        with patch("app.core.config.settings.settings") as settings:
            settings.seed_admin_enabled = True
            settings.seed_admin_email = "admin@ecommerce.local"
            settings.seed_admin_password = "Admin123!"
            settings.seed_admin_name = "Administrador"

            await seed_default_admin(session)

    repo.save.assert_awaited_once()
    saved_user = repo.save.await_args.args[0]
    assert saved_user.is_admin()
    assert str(saved_user.email) == "admin@ecommerce.local"
    assert saved_user.email_verified is True


@pytest.mark.asyncio
async def test_seed_default_admin_skips_when_exists() -> None:
    session = AsyncMock()
    existing = MagicMock()
    existing.scalar_one_or_none.return_value = "existing-id"
    session.execute = AsyncMock(return_value=existing)

    with patch("app.infra.repositories.user_repository.SqlAlchemyUserRepository") as repo_cls:
        repo = AsyncMock()
        repo_cls.return_value = repo
        with patch("app.core.config.settings.settings") as settings:
            settings.seed_admin_enabled = True

            await seed_default_admin(session)

    repo.save.assert_not_awaited()
