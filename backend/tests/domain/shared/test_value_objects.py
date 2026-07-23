import pytest

from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.email import Email
from app.domain.shared.value_objects.money import Money


class TestMoney:
    def test_from_decimal(self) -> None:
        money = Money.from_decimal("19.99")
        assert money.amount_cents == 1999
        assert str(money) == "19.99 BRL"

    def test_add_and_subtract(self) -> None:
        a = Money.from_decimal("10.00")
        b = Money.from_decimal("5.50")
        assert a.add(b).amount_cents == 1550
        assert a.subtract(Money.from_decimal("3.00")).amount_cents == 700

    def test_multiply(self) -> None:
        assert Money.from_decimal("2.50").multiply(3).amount_cents == 750

    def test_rejects_negative(self) -> None:
        with pytest.raises(DomainError):
            Money(-1)

    def test_currency_mismatch(self) -> None:
        with pytest.raises(DomainError):
            Money.from_decimal("1.00", "BRL").add(Money.from_decimal("1.00", "USD"))


class TestEmail:
    def test_create_normalizes(self) -> None:
        email = Email.create("  User@Example.COM ")
        assert str(email) == "user@example.com"

    def test_rejects_invalid(self) -> None:
        with pytest.raises(DomainError):
            Email.create("not-an-email")
