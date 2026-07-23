import pytest

from app.domain.coupon.entities.coupon import Coupon, DiscountType
from app.domain.inventory.entities.inventory_item import InventoryItem
from app.domain.payments.entities.payment import Payment, PaymentMethod, PaymentProvider
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.money import Money
from app.domain.shared.value_objects.sku import SKU


class TestCoupon:
    def test_percent_discount(self) -> None:
        coupon = Coupon.create(code="SAVE10", discount_type=DiscountType.PERCENT, discount_value=10)
        discount = coupon.calculate_discount(Money.from_decimal("100.00"))
        assert discount.amount_cents == 1000

    def test_fixed_discount(self) -> None:
        coupon = Coupon.create(code="OFF20", discount_type=DiscountType.FIXED, discount_value=2000)
        discount = coupon.calculate_discount(Money.from_decimal("100.00"))
        assert discount.amount_cents == 2000


class TestInventory:
    def test_reserve_stock(self) -> None:
        item = InventoryItem.create(
            product_id=EntityId.generate(),
            sku=SKU.create("SKU-001"),
            quantity=10,
        )
        item.reserve(3)
        assert item.quantity_available == 7
        assert item.quantity_reserved == 3

    def test_insufficient_stock(self) -> None:
        item = InventoryItem.create(
            product_id=EntityId.generate(),
            sku=SKU.create("SKU-002"),
            quantity=2,
        )
        with pytest.raises(DomainError):
            item.reserve(5)


class TestPayment:
    def test_payment_lifecycle(self) -> None:
        payment = Payment.create(
            order_id=EntityId.generate(),
            amount=Money.from_decimal("99.90"),
            method=PaymentMethod.PIX,
            provider=PaymentProvider.MOCK,
        )
        payment.mark_processing("ext_123", "https://pay.example.com")
        payment.approve()
        assert payment.is_approved()
