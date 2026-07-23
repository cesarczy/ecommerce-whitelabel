from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.interfaces.ports import CartRepository, OrderRepository
from app.infra.mappers.mappers import cart_to_domain, order_to_domain
from app.infra.models.models import (
    CartItemModel,
    CartModel,
    OrderItemModel,
    OrderModel,
    OrderStatusHistoryModel,
)


class SqlAlchemyCartRepository(CartRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, cart) -> None:
        result = await self._session.execute(
            select(CartModel).options(selectinload(CartModel.items)).where(CartModel.id == cart.id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            model = CartModel(
                id=cart.id.value,
                customer_id=cart.customer_id.value if cart.customer_id else None,
                session_id=cart.session_id,
                coupon_code=cart.coupon_code,
                created_at=cart.created_at,
                updated_at=cart.updated_at,
            )
            self._session.add(model)
        else:
            model.customer_id = cart.customer_id.value if cart.customer_id else None
            model.session_id = cart.session_id
            model.coupon_code = cart.coupon_code
            model.updated_at = cart.updated_at

        model.items.clear()
        for item in cart.items:
            model.items.append(
                CartItemModel(
                    id=item.id.value,
                    cart_id=cart.id.value,
                    product_id=item.product_id.value,
                    sku=str(item.sku),
                    product_name=item.product_name,
                    unit_price_cents=item.unit_price.amount_cents,
                    currency=item.unit_price.currency,
                    quantity=item.quantity,
                    added_at=item.added_at,
                )
            )
        await self._session.flush()

    async def find_by_id(self, cart_id: UUID):
        result = await self._session.execute(
            select(CartModel).options(selectinload(CartModel.items)).where(CartModel.id == cart_id)
        )
        model = result.scalar_one_or_none()
        return cart_to_domain(model) if model else None

    async def find_by_customer_id(self, customer_id: UUID):
        result = await self._session.execute(
            select(CartModel)
            .options(selectinload(CartModel.items))
            .where(CartModel.customer_id == customer_id)
            .order_by(CartModel.updated_at.desc())
        )
        model = result.scalars().first()
        return cart_to_domain(model) if model else None

    async def find_by_session_id(self, session_id: str):
        result = await self._session.execute(
            select(CartModel)
            .options(selectinload(CartModel.items))
            .where(CartModel.session_id == session_id)
            .order_by(CartModel.updated_at.desc())
        )
        model = result.scalars().first()
        return cart_to_domain(model) if model else None


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, order) -> None:
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items), selectinload(OrderModel.status_history))
            .where(OrderModel.id == order.id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            model = OrderModel(id=order.id.value)
            self._session.add(model)

        model.order_number = str(order.order_number)
        model.customer_id = order.customer_id.value
        model.status = order.status.value
        model.subtotal_cents = order.subtotal.amount_cents
        model.discount_cents = order.discount.amount_cents
        model.shipping_cost_cents = order.shipping_cost.amount_cents
        model.total_cents = order.total.amount_cents
        model.currency = order.total.currency
        model.coupon_id = order.coupon_id.value if order.coupon_id else None
        model.payment_id = order.payment_id.value if order.payment_id else None
        model.shipping_street = order.shipping_address.street
        model.shipping_number = order.shipping_address.number
        model.shipping_complement = order.shipping_address.complement
        model.shipping_neighborhood = order.shipping_address.neighborhood
        model.shipping_city = order.shipping_address.city
        model.shipping_state = order.shipping_address.state
        model.shipping_cep = order.shipping_address.cep.value
        model.created_at = order.created_at
        model.updated_at = order.updated_at

        model.items.clear()
        for item in order.items:
            model.items.append(
                OrderItemModel(
                    id=item.id.value,
                    order_id=order.id.value,
                    product_id=item.product_id.value,
                    sku=str(item.sku),
                    product_name=item.product_name,
                    unit_price_cents=item.unit_price.amount_cents,
                    currency=item.unit_price.currency,
                    quantity=item.quantity,
                )
            )

        model.status_history.clear()
        for entry in order.status_history:
            model.status_history.append(
                OrderStatusHistoryModel(
                    order_id=order.id.value,
                    status=entry.status.value,
                    note=entry.note,
                    changed_at=entry.changed_at,
                )
            )
        await self._session.flush()

    async def find_by_id(self, order_id: UUID):
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items), selectinload(OrderModel.status_history))
            .where(OrderModel.id == order_id)
        )
        model = result.scalar_one_or_none()
        return order_to_domain(model) if model else None

    async def find_by_customer_id(self, customer_id: UUID, *, limit: int = 20) -> list:
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items), selectinload(OrderModel.status_history))
            .where(OrderModel.customer_id == customer_id)
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
        )
        return [order_to_domain(model) for model in result.scalars().all()]
