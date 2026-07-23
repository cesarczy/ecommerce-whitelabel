from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from app.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True)
class UserRegisteredEvent(DomainEvent):
    email: str
    full_name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UserEmailVerifiedEvent(DomainEvent):
    email: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UserPasswordChangedEvent(DomainEvent):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class UserDeactivatedEvent(DomainEvent):
    reason: str | None = None
