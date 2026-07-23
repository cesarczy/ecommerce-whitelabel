from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError


@dataclass
class Role:
    id: EntityId
    name: str
    permissions: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, name: str, permissions: list[str] | None = None) -> Role:
        normalized = name.strip().lower()
        if not normalized:
            raise DomainError("Role name cannot be empty", code="INVALID_ROLE")
        return cls(
            id=EntityId.generate(),
            name=normalized,
            permissions=sorted(set(permissions or [])),
        )

    @classmethod
    def reconstitute(
        cls,
        role_id: EntityId,
        name: str,
        permissions: list[str],
    ) -> Role:
        return cls(id=role_id, name=name, permissions=permissions)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def grant_permission(self, permission: str) -> None:
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.permissions.sort()

    def revoke_permission(self, permission: str) -> None:
        if permission in self.permissions:
            self.permissions.remove(permission)


CUSTOMER_ROLE = Role.reconstitute(
    EntityId.from_string("00000000-0000-4000-8000-000000000001"),
    "customer",
    ["orders:read", "profile:write"],
)

ADMIN_ROLE = Role.reconstitute(
    EntityId.from_string("00000000-0000-4000-8000-000000000002"),
    "admin",
    ["*"],
)

STAFF_ROLE = Role.reconstitute(
    EntityId.from_string("00000000-0000-4000-8000-000000000003"),
    "staff",
    ["products:read", "orders:read", "orders:write", "inventory:write"],
)
