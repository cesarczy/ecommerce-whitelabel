from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.money import Money
from app.domain.shared.domain_event import DomainEvent


class PaymentMethod(StrEnum):
    PIX = "pix"
    CREDIT_CARD = "credit_card"
    BOLETO = "boleto"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"


class PaymentProvider(StrEnum):
    MERCADO_PAGO = "mercado_pago"
    STRIPE = "stripe"
    MOCK = "mock"


@dataclass(frozen=True, slots=True, kw_only=True)
class PaymentCreatedEvent(DomainEvent):
    order_id: str
    amount_cents: int
    provider: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PaymentConfirmedEvent(DomainEvent):
    order_id: str
    external_id: str


@dataclass
class Payment(AggregateRoot):
    id: EntityId
    order_id: EntityId
    amount: Money
    method: PaymentMethod
    provider: PaymentProvider
    status: PaymentStatus
    external_id: str | None
    checkout_url: str | None
    metadata: dict
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        super().__init__()

    @classmethod
    def create(
        cls,
        *,
        order_id: EntityId,
        amount: Money,
        method: PaymentMethod,
        provider: PaymentProvider,
    ) -> Payment:
        now = datetime.now(UTC)
        payment = cls(
            id=EntityId.generate(),
            order_id=order_id,
            amount=amount,
            method=method,
            provider=provider,
            status=PaymentStatus.PENDING,
            external_id=None,
            checkout_url=None,
            metadata={},
            created_at=now,
            updated_at=now,
        )
        payment._record_event(
            PaymentCreatedEvent(
                aggregate_id=payment.id.value,
                order_id=str(order_id.value),
                amount_cents=amount.amount_cents,
                provider=provider.value,
            )
        )
        return payment

    @classmethod
    def reconstitute(
        cls,
        *,
        payment_id: EntityId,
        order_id: EntityId,
        amount: Money,
        method: PaymentMethod,
        provider: PaymentProvider,
        status: PaymentStatus,
        external_id: str | None,
        checkout_url: str | None,
        metadata: dict,
        created_at: datetime,
        updated_at: datetime,
    ) -> Payment:
        return cls(
            id=payment_id,
            order_id=order_id,
            amount=amount,
            method=method,
            provider=provider,
            status=status,
            external_id=external_id,
            checkout_url=checkout_url,
            metadata=metadata,
            created_at=created_at,
            updated_at=updated_at,
        )

    def mark_processing(self, external_id: str, checkout_url: str | None = None) -> None:
        self.status = PaymentStatus.PROCESSING
        self.external_id = external_id
        self.checkout_url = checkout_url
        self.updated_at = datetime.now(UTC)

    def approve(self) -> None:
        if self.status == PaymentStatus.APPROVED:
            return
        self.status = PaymentStatus.APPROVED
        self.updated_at = datetime.now(UTC)
        self._record_event(
            PaymentConfirmedEvent(
                aggregate_id=self.id.value,
                order_id=str(self.order_id.value),
                external_id=self.external_id or "",
            )
        )

    def reject(self, reason: str) -> None:
        self.status = PaymentStatus.REJECTED
        self.metadata = {**self.metadata, "reject_reason": reason}
        self.updated_at = datetime.now(UTC)

    def is_approved(self) -> bool:
        return self.status == PaymentStatus.APPROVED
