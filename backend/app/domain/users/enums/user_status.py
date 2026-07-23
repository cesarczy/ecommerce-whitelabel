from enum import StrEnum


class UserStatus(StrEnum):
    PENDING_EMAIL = "pending_email"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
