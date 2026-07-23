from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, slots=True, kw_only=True)
class TenantCreatedEvent(DomainEvent):
    slug: str
    name: str


@dataclass
class Tenant(AggregateRoot):
    id: EntityId
    slug: str
    name: str
    domain: str | None
    is_active: bool
    created_at: datetime

    def __post_init__(self) -> None:
        super().__init__()

    @classmethod
    def create(cls, *, slug: str, name: str, domain: str | None = None) -> Tenant:
        normalized_slug = slug.strip().lower()
        if not normalized_slug or len(normalized_slug) < 2:
            raise DomainError("Tenant slug must have at least 2 characters", code="INVALID_TENANT")
        now = datetime.now(UTC)
        tenant = cls(
            id=EntityId.generate(),
            slug=normalized_slug,
            name=name.strip(),
            domain=domain.strip() if domain else None,
            is_active=True,
            created_at=now,
        )
        tenant._record_event(
            TenantCreatedEvent(aggregate_id=tenant.id.value, slug=normalized_slug, name=tenant.name)
        )
        return tenant

    @classmethod
    def reconstitute(
        cls,
        *,
        tenant_id: EntityId,
        slug: str,
        name: str,
        domain: str | None,
        is_active: bool,
        created_at: datetime,
    ) -> Tenant:
        return cls(
            id=tenant_id,
            slug=slug,
            name=name,
            domain=domain,
            is_active=is_active,
            created_at=created_at,
        )

    def deactivate(self) -> None:
        self.is_active = False
