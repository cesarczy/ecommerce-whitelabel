from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.domain_event import DomainEvent
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError


@dataclass(frozen=True, slots=True, kw_only=True)
class StoreConfiguredEvent(DomainEvent):
    name: str
    primary_color: str


@dataclass
class StoreSettings(AggregateRoot):
    id: EntityId
    tenant_id: EntityId
    name: str
    tagline: str
    logo_url: str | None
    primary_color: str
    secondary_color: str
    support_email: str | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        super().__init__()

    @classmethod
    def create(
        cls,
        *,
        tenant_id: EntityId,
        name: str,
        tagline: str = "",
        primary_color: str = "#4F46E5",
        secondary_color: str = "#6366F1",
    ) -> StoreSettings:
        if not name.strip():
            raise DomainError("Store name is required", code="INVALID_STORE")
        now = datetime.now(UTC)
        store = cls(
            id=EntityId.generate(),
            tenant_id=tenant_id,
            name=name.strip(),
            tagline=tagline.strip(),
            logo_url=None,
            primary_color=primary_color,
            secondary_color=secondary_color,
            support_email=None,
            created_at=now,
            updated_at=now,
        )
        store._record_event(
            StoreConfiguredEvent(
                aggregate_id=store.id.value,
                name=store.name,
                primary_color=store.primary_color,
            )
        )
        return store

    def update_branding(
        self,
        *,
        name: str | None = None,
        tagline: str | None = None,
        logo_url: str | None = None,
        primary_color: str | None = None,
        secondary_color: str | None = None,
    ) -> None:
        if name is not None:
            self.name = name.strip()
        if tagline is not None:
            self.tagline = tagline.strip()
        if logo_url is not None:
            self.logo_url = logo_url.strip() or None
        if primary_color is not None:
            self.primary_color = primary_color
        if secondary_color is not None:
            self.secondary_color = secondary_color
        self.updated_at = datetime.now(UTC)


@dataclass
class Banner:
    id: EntityId
    title: str
    image_key: str
    link_url: str | None
    sort_order: int
    is_active: bool

    @classmethod
    def create(cls, *, title: str, image_key: str, link_url: str | None = None, sort_order: int = 0) -> Banner:
        return cls(
            id=EntityId.generate(),
            title=title.strip(),
            image_key=image_key.strip(),
            link_url=link_url.strip() if link_url else None,
            sort_order=sort_order,
            is_active=True,
        )
