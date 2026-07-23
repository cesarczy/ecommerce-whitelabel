import pytest

from app.application.commands.auth import RegisterUserUseCase
from app.application.dto.schemas import RegisterUserInput
from app.application.exceptions import ConflictError
from app.domain.users.entities.user import User


class FakeUserRepo:
    def __init__(self) -> None:
        self.saved: list[User] = []
        self._emails: set[str] = set()

    async def save(self, user: User) -> None:
        self.saved.append(user)
        self._emails.add(str(user.email))

    async def find_by_id(self, user_id):
        return None

    async def find_by_email(self, email: str):
        return None

    async def exists_by_email(self, email: str) -> bool:
        return email.lower() in self._emails


class FakeUoW:
    def __init__(self) -> None:
        self.users = FakeUserRepo()

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


class FakeHasher:
    def hash(self, plain_password: str) -> str:
        return f"hashed:{plain_password}"

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{plain_password}"


class FakeEventBus:
    def __init__(self) -> None:
        self.events = []

    async def publish(self, events) -> None:
        self.events.extend(events)


@pytest.mark.asyncio
async def test_register_user_success() -> None:
    uow = FakeUoW()
    bus = FakeEventBus()
    use_case = RegisterUserUseCase(uow, FakeHasher(), bus)
    result = await use_case.execute(
        RegisterUserInput(email="user@example.com", full_name="Test User", password="password123")
    )
    assert result.email == "user@example.com"
    assert len(uow.users.saved) == 1
    assert len(bus.events) == 1


@pytest.mark.asyncio
async def test_register_user_conflict() -> None:
    uow = FakeUoW()
    uow.users._emails.add("user@example.com")
    use_case = RegisterUserUseCase(uow, FakeHasher(), FakeEventBus())
    with pytest.raises(ConflictError):
        await use_case.execute(
            RegisterUserInput(email="user@example.com", full_name="Test User", password="password123")
        )
