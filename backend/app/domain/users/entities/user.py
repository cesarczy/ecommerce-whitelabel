from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.email import Email
from app.domain.shared.value_objects.phone import Phone
from app.domain.users.entities.role import ADMIN_ROLE, CUSTOMER_ROLE, STAFF_ROLE, Role
from app.domain.users.entities.user_address import UserAddress
from app.domain.users.enums.user_status import UserStatus
from app.domain.users.events.user_events import (
    UserDeactivatedEvent,
    UserEmailVerifiedEvent,
    UserPasswordChangedEvent,
    UserRegisteredEvent,
)


@dataclass
class User(AggregateRoot):
    id: EntityId
    email: Email
    full_name: str
    password_hash: str
    phone: Phone | None
    status: UserStatus
    email_verified: bool
    mfa_enabled: bool
    roles: list[Role]
    addresses: list[UserAddress]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        super().__init__()

    @classmethod
    def create(
        cls,
        *,
        email: str | Email,
        full_name: str,
        password_hash: str,
        phone: str | Phone | None = None,
        roles: list[Role] | None = None,
    ) -> User:
        email_vo = email if isinstance(email, Email) else Email.create(email)
        name = full_name.strip()
        if len(name) < 2:
            raise DomainError("Full name must have at least 2 characters", code="INVALID_USER")
        if not password_hash:
            raise DomainError("Password hash is required", code="INVALID_USER")

        phone_vo: Phone | None = None
        if phone is not None:
            phone_vo = phone if isinstance(phone, Phone) else Phone.create(phone)

        now = datetime.now(UTC)
        user = cls(
            id=EntityId.generate(),
            email=email_vo,
            full_name=name,
            password_hash=password_hash,
            phone=phone_vo,
            status=UserStatus.PENDING_EMAIL,
            email_verified=False,
            mfa_enabled=False,
            roles=list(roles or [CUSTOMER_ROLE]),
            addresses=[],
            created_at=now,
            updated_at=now,
        )
        user._record_event(
            UserRegisteredEvent(
                aggregate_id=user.id.value,
                email=str(email_vo),
                full_name=name,
            )
        )
        return user

    @classmethod
    def reconstitute(
        cls,
        *,
        user_id: EntityId,
        email: Email,
        full_name: str,
        password_hash: str,
        phone: Phone | None,
        status: UserStatus,
        email_verified: bool,
        mfa_enabled: bool,
        roles: list[Role],
        addresses: list[UserAddress],
        created_at: datetime,
        updated_at: datetime,
    ) -> User:
        return cls(
            id=user_id,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            phone=phone,
            status=status,
            email_verified=email_verified,
            mfa_enabled=mfa_enabled,
            roles=roles,
            addresses=addresses,
            created_at=created_at,
            updated_at=updated_at,
        )

    def update_profile(self, *, full_name: str | None = None, phone: str | Phone | None = ...) -> None:
        self._ensure_active()
        if full_name is not None:
            name = full_name.strip()
            if len(name) < 2:
                raise DomainError("Full name must have at least 2 characters", code="INVALID_USER")
            self.full_name = name
        if phone is not ...:
            if phone is None:
                self.phone = None
            else:
                self.phone = phone if isinstance(phone, Phone) else Phone.create(phone)
        self.updated_at = datetime.now(UTC)

    def change_password(self, new_password_hash: str) -> None:
        self._ensure_active()
        if not new_password_hash:
            raise DomainError("Password hash is required", code="INVALID_USER")
        self.password_hash = new_password_hash
        self.updated_at = datetime.now(UTC)
        self._record_event(UserPasswordChangedEvent(aggregate_id=self.id.value))

    def verify_email(self) -> None:
        if self.email_verified:
            return
        self.email_verified = True
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.now(UTC)
        self._record_event(UserEmailVerifiedEvent(aggregate_id=self.id.value, email=str(self.email)))

    def enable_mfa(self) -> None:
        self._ensure_active()
        if self.mfa_enabled:
            return
        if not self.email_verified:
            raise DomainError("Email must be verified before enabling MFA", code="MFA_NOT_ALLOWED")
        self.mfa_enabled = True
        self.updated_at = datetime.now(UTC)

    def disable_mfa(self) -> None:
        self.mfa_enabled = False
        self.updated_at = datetime.now(UTC)

    def add_address(self, address: Address, *, is_default: bool = False) -> UserAddress:
        self._ensure_active()
        user_address = UserAddress.create(address, is_default=is_default)
        if is_default or not self.addresses:
            for existing in self.addresses:
                existing.is_default = False
            user_address.is_default = True
        self.addresses.append(user_address)
        self.updated_at = datetime.now(UTC)
        return user_address

    def remove_address(self, address_id: EntityId) -> None:
        self._ensure_active()
        before = len(self.addresses)
        self.addresses = [addr for addr in self.addresses if addr.id.value != address_id.value]
        if len(self.addresses) == before:
            raise DomainError("Address not found", code="ADDRESS_NOT_FOUND")
        if self.addresses and not any(addr.is_default for addr in self.addresses):
            self.addresses[0].is_default = True
        self.updated_at = datetime.now(UTC)

    def assign_role(self, role: Role) -> None:
        self._ensure_active()
        if any(existing.name == role.name for existing in self.roles):
            return
        self.roles.append(role)
        self.updated_at = datetime.now(UTC)

    def has_permission(self, permission: str) -> bool:
        for role in self.roles:
            if "*" in role.permissions or role.has_permission(permission):
                return True
        return False

    def is_admin(self) -> bool:
        return any(role.name == ADMIN_ROLE.name for role in self.roles)

    def is_customer(self) -> bool:
        return any(role.name == CUSTOMER_ROLE.name for role in self.roles)

    def is_staff(self) -> bool:
        return any(role.name == STAFF_ROLE.name for role in self.roles)

    def deactivate(self, reason: str | None = None) -> None:
        if self.status == UserStatus.INACTIVE:
            return
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.now(UTC)
        self._record_event(UserDeactivatedEvent(aggregate_id=self.id.value, reason=reason))

    def suspend(self) -> None:
        self._ensure_active()
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.now(UTC)

    def get_default_address(self) -> UserAddress | None:
        for address in self.addresses:
            if address.is_default:
                return address
        return None

    def _ensure_active(self) -> None:
        if self.status in (UserStatus.INACTIVE, UserStatus.SUSPENDED):
            raise DomainError("User is not active", code="USER_NOT_ACTIVE")
