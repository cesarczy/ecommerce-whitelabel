import pytest

from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.money import Money
from app.domain.shared.value_objects.sku import SKU
from app.domain.orders.entities.cart import Cart
from app.domain.orders.entities.order import Order
from app.domain.orders.enums.order_status import OrderStatus
from app.domain.orders.events.order_events import OrderCreatedEvent, OrderPaidEvent


class TestCart:
    def test_add_item_and_calculate_subtotal(self) -> None:
        cart = Cart.create(session_id="sess-123")
        product_id = EntityId.generate()
        cart.add_item(
            product_id=product_id,
            sku=SKU.create("PROD-001"),
            product_name="Produto Teste",
            unit_price=Money.from_decimal("10.00"),
            quantity=2,
        )
        assert cart.item_count == 2
        assert cart.subtotal.amount_cents == 2000

    def test_merge_same_sku_increases_quantity(self) -> None:
        cart = Cart.create(session_id="sess-456")
        product_id = EntityId.generate()
        sku = SKU.create("PROD-002")
        cart.add_item(
            product_id=product_id,
            sku=sku,
            product_name="Produto",
            unit_price=Money.from_decimal("5.00"),
            quantity=1,
        )
        cart.add_item(
            product_id=product_id,
            sku=sku,
            product_name="Produto",
            unit_price=Money.from_decimal("5.00"),
            quantity=2,
        )
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 3


class TestOrder:
    def test_create_from_cart(self) -> None:
        customer_id = EntityId.generate()
        cart = Cart.create(customer_id=customer_id)
        product_id = EntityId.generate()
        cart.add_item(
            product_id=product_id,
            sku=SKU.create("ORD-001"),
            product_name="Item",
            unit_price=Money.from_decimal("100.00"),
            quantity=1,
        )
        address = Address.create(
            street="Rua B",
            number="50",
            neighborhood="Jardins",
            city="São Paulo",
            state="SP",
            cep="01415000",
        )
        order = Order.create_from_cart(
            customer_id=customer_id,
            cart=cart,
            shipping_address=address,
            shipping_cost=Money.from_decimal("15.00"),
        )
        events = order.collect_events()
        assert isinstance(events[0], OrderCreatedEvent)
        assert order.total.amount_cents == 11500
        assert order.status == OrderStatus.CREATED

    def test_mark_paid_transitions_status(self) -> None:
        customer_id = EntityId.generate()
        cart = Cart.create(customer_id=customer_id)
        cart.add_item(
            product_id=EntityId.generate(),
            sku=SKU.create("ORD-002"),
            product_name="Item",
            unit_price=Money.from_decimal("50.00"),
            quantity=1,
        )
        order = Order.create_from_cart(
            customer_id=customer_id,
            cart=cart,
            shipping_address=Address.create(
                street="Rua C",
                number="1",
                neighborhood="Centro",
                city="SP",
                state="SP",
                cep="01310100",
            ),
            shipping_cost=Money.zero(),
        )
        order.collect_events()
        order.mark_awaiting_payment()
        payment_id = EntityId.generate()
        order.mark_paid(payment_id)
        assert order.status == OrderStatus.PAID
        assert order.payment_id == payment_id
        events = order.collect_events()
        assert any(isinstance(e, OrderPaidEvent) for e in events)

    def test_cannot_cancel_delivered_order(self) -> None:
        customer_id = EntityId.generate()
        cart = Cart.create(customer_id=customer_id)
        cart.add_item(
            product_id=EntityId.generate(),
            sku=SKU.create("ORD-003"),
            product_name="Item",
            unit_price=Money.from_decimal("20.00"),
            quantity=1,
        )
        order = Order.create_from_cart(
            customer_id=customer_id,
            cart=cart,
            shipping_address=Address.create(
                street="Rua D",
                number="2",
                neighborhood="Centro",
                city="SP",
                state="SP",
                cep="01310100",
            ),
            shipping_cost=Money.zero(),
        )
        order.mark_awaiting_payment()
        order.mark_paid(EntityId.generate())
        order.mark_processing()
        order.mark_shipped()
        order.mark_delivered()
        with pytest.raises(DomainError):
            order.cancel()
