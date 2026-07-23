from uuid import UUID

from app.application.dto.schemas import AddToCartInput, CartItemOutput, CartOutput, CheckoutInput, OrderOutput
from app.application.exceptions import NotFoundError
from app.application.interfaces.ports import EventBus, UnitOfWork
from app.domain.orders.entities.cart import Cart
from app.domain.orders.entities.order import Order
from app.domain.shared.entity_id import EntityId
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.money import Money
from app.domain.shared.value_objects.sku import SKU


class GetCartUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, cart_id: UUID | None = None, session_id: str | None = None) -> CartOutput:
        cart = None
        if cart_id:
            cart = await self._uow.carts.find_by_id(cart_id)
        elif session_id:
            cart = await self._uow.carts.find_by_session_id(session_id)
        if cart is None:
            raise NotFoundError("Cart not found")
        return _to_cart_output(cart)


class AddToCartUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(
        self,
        data: AddToCartInput,
        *,
        customer_id: UUID | None = None,
    ) -> CartOutput:
        product = await self._uow.products.find_by_id(UUID(data.product_id))
        if product is None or not product.is_available():
            raise NotFoundError("Product not available")

        cart = None
        if customer_id:
            cart = await self._uow.carts.find_by_customer_id(customer_id)
        elif data.session_id:
            cart = await self._uow.carts.find_by_session_id(data.session_id)

        if cart is None:
            cart = Cart.create(
                customer_id=EntityId.from_string(str(customer_id)) if customer_id else None,
                session_id=data.session_id,
            )

        unit_price = product.resolve_price(SKU.create(data.sku))
        cart.add_item(
            product_id=product.id,
            sku=SKU.create(data.sku),
            product_name=str(product.name),
            unit_price=unit_price,
            quantity=data.quantity,
        )
        await self._uow.carts.save(cart)
        events = cart.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return _to_cart_output(cart)


class CheckoutUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, customer_id: UUID, data: CheckoutInput) -> OrderOutput:
        cart = await self._uow.carts.find_by_id(UUID(data.cart_id))
        if cart is None or cart.is_empty():
            raise NotFoundError("Cart not found or empty")

        shipping_address = Address.create(
            street=data.shipping_address.street,
            number=data.shipping_address.number,
            complement=data.shipping_address.complement,
            neighborhood=data.shipping_address.neighborhood,
            city=data.shipping_address.city,
            state=data.shipping_address.state,
            cep=data.shipping_address.cep,
            label=data.shipping_address.label,
        )
        order = Order.create_from_cart(
            customer_id=EntityId.from_string(str(customer_id)),
            cart=cart,
            shipping_address=shipping_address,
            shipping_cost=Money.from_decimal(data.shipping_cost),
        )
        order.mark_awaiting_payment()
        await self._uow.orders.save(order)
        cart.clear()
        await self._uow.carts.save(cart)
        events = order.collect_events() + cart.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return _to_order_output(order)


def _to_cart_output(cart: Cart) -> CartOutput:
    items = [
        CartItemOutput(
            id=str(item.id.value),
            product_id=str(item.product_id.value),
            sku=str(item.sku),
            product_name=item.product_name,
            unit_price=str(item.unit_price.to_decimal()),
            quantity=item.quantity,
            line_total=str(item.line_total.to_decimal()),
        )
        for item in cart.items
    ]
    return CartOutput(
        id=str(cart.id.value),
        items=items,
        subtotal=str(cart.subtotal.to_decimal()),
        item_count=cart.item_count,
    )


def _to_order_output(order: Order) -> OrderOutput:
    items = [
        CartItemOutput(
            id=str(item.id.value),
            product_id=str(item.product_id.value),
            sku=str(item.sku),
            product_name=item.product_name,
            unit_price=str(item.unit_price.to_decimal()),
            quantity=item.quantity,
            line_total=str(item.line_total.to_decimal()),
        )
        for item in order.items
    ]
    return OrderOutput(
        id=str(order.id.value),
        order_number=str(order.order_number),
        status=order.status.value,
        subtotal=str(order.subtotal.to_decimal()),
        discount=str(order.discount.to_decimal()),
        shipping_cost=str(order.shipping_cost.to_decimal()),
        total=str(order.total.to_decimal()),
        items=items,
    )
