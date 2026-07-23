from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.shared.domain_event import DomainEvent
from app.domain.users.entities.user import User


class Clock(Protocol):
    def now(self) -> datetime: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, events: list[DomainEvent]) -> None: ...


class StoragePort(ABC):
    @abstractmethod
    async def upload(self, *, key: str, data: bytes, content_type: str) -> str: ...

    @abstractmethod
    async def get_presigned_url(self, *, key: str, expires_seconds: int = 3600) -> str: ...

    @abstractmethod
    async def delete(self, *, key: str) -> None: ...


@dataclass
class PaymentGatewayRequest:
    order_id: UUID
    amount_cents: int
    currency: str
    method: str
    customer_email: str
    description: str


@dataclass
class PaymentGatewayResponse:
    external_id: str
    checkout_url: str | None
    status: str
    raw: dict


class PaymentGatewayPort(ABC):
    @abstractmethod
    async def create_payment(self, request: PaymentGatewayRequest) -> PaymentGatewayResponse: ...

    @abstractmethod
    async def get_payment_status(self, external_id: str) -> str: ...


class OAuthUserInfo:
    def __init__(self, provider: str, provider_user_id: str, email: str, name: str) -> None:
        self.provider = provider
        self.provider_user_id = provider_user_id
        self.email = email
        self.name = name


class OAuthProviderPort(ABC):
    @abstractmethod
    def get_authorization_url(self, *, state: str) -> str: ...

    @abstractmethod
    async def exchange_code(self, code: str) -> OAuthUserInfo: ...


class UnitOfWork(ABC):
    users: "UserRepository"
    products: "ProductRepository"
    carts: "CartRepository"
    orders: "OrderRepository"
    payments: "PaymentRepository"
    coupons: "CouponRepository"
    inventory: "InventoryRepository"
    tenants: "TenantRepository"

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    async def __aenter__(self) -> "UnitOfWork": ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...


class TenantRepository(ABC):
    @abstractmethod
    async def save(self, tenant) -> None: ...

    @abstractmethod
    async def find_by_slug(self, slug: str): ...

    @abstractmethod
    async def find_by_id(self, tenant_id: UUID): ...


class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None: ...

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool: ...


class ProductRepository(ABC):
    @abstractmethod
    async def save(self, product) -> None: ...

    @abstractmethod
    async def find_by_id(self, product_id: UUID): ...

    @abstractmethod
    async def find_by_slug(self, slug: str): ...

    @abstractmethod
    async def list_active(self, *, offset: int = 0, limit: int = 20) -> list: ...


class CartRepository(ABC):
    @abstractmethod
    async def save(self, cart) -> None: ...

    @abstractmethod
    async def find_by_id(self, cart_id: UUID): ...

    @abstractmethod
    async def find_by_customer_id(self, customer_id: UUID): ...

    @abstractmethod
    async def find_by_session_id(self, session_id: str): ...


class OrderRepository(ABC):
    @abstractmethod
    async def save(self, order) -> None: ...

    @abstractmethod
    async def find_by_id(self, order_id: UUID): ...

    @abstractmethod
    async def find_by_customer_id(self, customer_id: UUID, *, limit: int = 20) -> list: ...


class PaymentRepository(ABC):
    @abstractmethod
    async def save(self, payment) -> None: ...

    @abstractmethod
    async def find_by_id(self, payment_id: UUID): ...

    @abstractmethod
    async def find_by_order_id(self, order_id: UUID): ...

    @abstractmethod
    async def find_by_external_id(self, external_id: str): ...


class CouponRepository(ABC):
    @abstractmethod
    async def save(self, coupon) -> None: ...

    @abstractmethod
    async def find_by_code(self, code: str): ...

    @abstractmethod
    async def find_by_id(self, coupon_id: UUID): ...

    @abstractmethod
    async def list_active(self) -> list: ...


class InventoryRepository(ABC):
    @abstractmethod
    async def save(self, item) -> None: ...

    @abstractmethod
    async def find_by_sku(self, sku: str): ...

    @abstractmethod
    async def find_low_stock(self) -> list: ...


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain_password: str) -> str: ...

    @abstractmethod
    def verify(self, plain_password: str, password_hash: str) -> bool: ...


class TokenPair:
    def __init__(self, access_token: str, refresh_token: str, expires_in: int) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in


class TokenService(ABC):
    @abstractmethod
    def create_tokens(self, user_id: UUID, roles: list[str]) -> TokenPair: ...

    @abstractmethod
    def verify_access_token(self, token: str) -> dict: ...

    @abstractmethod
    def verify_refresh_token(self, token: str) -> dict: ...

    @abstractmethod
    def rotate_refresh_token(self, refresh_token: str) -> TokenPair: ...


class RefreshTokenStore(ABC):
    @abstractmethod
    async def store(self, user_id: UUID, token: str, expires_at: datetime) -> None: ...

    @abstractmethod
    async def revoke(self, token: str) -> None: ...

    @abstractmethod
    async def is_valid(self, user_id: UUID, token: str) -> bool: ...


class MfaService(ABC):
    @abstractmethod
    def generate_secret(self) -> str: ...

    @abstractmethod
    def get_provisioning_uri(self, *, secret: str, email: str) -> str: ...

    @abstractmethod
    def verify_code(self, *, secret: str, code: str) -> bool: ...
