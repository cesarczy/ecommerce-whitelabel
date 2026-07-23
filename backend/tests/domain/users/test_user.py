import pytest

from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.address import Address
from app.domain.users.entities.role import ADMIN_ROLE
from app.domain.users.entities.user import User
from app.domain.users.enums.user_status import UserStatus
from app.domain.users.events.user_events import UserRegisteredEvent


class TestUser:
    def test_create_emits_registered_event(self) -> None:
        user = User.create(
            email="cesarczy@gmail.com",
            full_name="César Siqueira",
            password_hash="hashed-password",
            phone="11999999999",
        )
        events = user.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], UserRegisteredEvent)
        assert user.status == UserStatus.PENDING_EMAIL

    def test_verify_email_activates_user(self) -> None:
        user = User.create(
            email="user@example.com",
            full_name="Test User",
            password_hash="hash",
        )
        user.collect_events()
        user.verify_email()
        assert user.email_verified is True
        assert user.status == UserStatus.ACTIVE

    def test_mfa_requires_verified_email(self) -> None:
        user = User.create(
            email="user@example.com",
            full_name="Test User",
            password_hash="hash",
        )
        with pytest.raises(DomainError):
            user.enable_mfa()

    def test_add_address_sets_default(self) -> None:
        user = User.create(
            email="user@example.com",
            full_name="Test User",
            password_hash="hash",
        )
        user.verify_email()
        address = Address.create(
            street="Rua A",
            number="10",
            neighborhood="Centro",
            city="SP",
            state="SP",
            cep="01310100",
        )
        user_address = user.add_address(address, is_default=True)
        assert user_address.is_default is True
        assert user.get_default_address() is user_address

    def test_admin_permission(self) -> None:
        user = User.create(
            email="admin@example.com",
            full_name="Admin User",
            password_hash="hash",
            roles=[ADMIN_ROLE],
        )
        assert user.has_permission("products:write") is True
