from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.domain.shared.exceptions import DomainError

SUPPORTED_CURRENCIES = frozenset({"BRL", "USD"})


@dataclass(frozen=True, slots=True)
class Money:
    amount_cents: int
    currency: str = "BRL"

    def __post_init__(self) -> None:
        currency = self.currency.upper()
        object.__setattr__(self, "currency", currency)
        if currency not in SUPPORTED_CURRENCIES:
            raise DomainError(f"Unsupported currency: {currency}", code="INVALID_CURRENCY")
        if self.amount_cents < 0:
            raise DomainError("Money amount cannot be negative", code="INVALID_MONEY")

    @classmethod
    def from_decimal(cls, amount: Decimal | float | str, currency: str = "BRL") -> Money:
        decimal_amount = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        cents = int(decimal_amount * 100)
        return cls(cents, currency)

    @classmethod
    def zero(cls, currency: str = "BRL") -> Money:
        return cls(0, currency)

    def to_decimal(self) -> Decimal:
        return Decimal(self.amount_cents) / Decimal(100)

    def add(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return Money(self.amount_cents + other.amount_cents, self.currency)

    def subtract(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        result = self.amount_cents - other.amount_cents
        if result < 0:
            raise DomainError("Money subtraction would result in negative amount", code="INVALID_MONEY")
        return Money(result, self.currency)

    def multiply(self, factor: int) -> Money:
        if factor < 0:
            raise DomainError("Multiplication factor cannot be negative", code="INVALID_MONEY")
        return Money(self.amount_cents * factor, self.currency)

    def equals(self, other: Money) -> bool:
        return self.amount_cents == other.amount_cents and self.currency == other.currency

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise DomainError(
                f"Currency mismatch: {self.currency} vs {other.currency}",
                code="CURRENCY_MISMATCH",
            )

    def __str__(self) -> str:
        return f"{self.to_decimal():.2f} {self.currency}"
