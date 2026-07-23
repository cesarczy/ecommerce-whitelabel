from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.schemas import AnalyticsReportOutput
from app.core.context.tenant import get_current_tenant_id
from app.core.middlewares.tenant import DEFAULT_TENANT_ID
from app.infra.models.models import CartModel, FavoriteModel, OrderModel, PaymentModel, ReviewModel, UserModel


class GetAnalyticsReportQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self) -> AnalyticsReportOutput:
        tenant_id = get_current_tenant_id() or DEFAULT_TENANT_ID

        sales_result = await self._session.execute(
            select(func.coalesce(func.sum(PaymentModel.amount_cents), 0)).where(
                PaymentModel.tenant_id == tenant_id,
                PaymentModel.status == "approved",
            )
        )
        total_sales_cents = int(sales_result.scalar_one())

        orders_result = await self._session.execute(
            select(func.count(OrderModel.id)).where(OrderModel.status != "cancelled")
        )
        orders_count = int(orders_result.scalar_one())

        carts_result = await self._session.execute(select(func.count(CartModel.id)))
        carts_count = int(carts_result.scalar_one())

        customers_result = await self._session.execute(select(func.count(UserModel.id)))
        customers_count = int(customers_result.scalar_one())

        favorites_result = await self._session.execute(
            select(func.count(FavoriteModel.id)).where(FavoriteModel.tenant_id == tenant_id)
        )
        favorites_count = int(favorites_result.scalar_one())

        reviews_result = await self._session.execute(
            select(func.count(ReviewModel.id)).where(ReviewModel.tenant_id == tenant_id)
        )
        reviews_count = int(reviews_result.scalar_one())

        conversion = (orders_count / carts_count * 100) if carts_count else 0.0
        avg_ticket = total_sales_cents / orders_count if orders_count else 0

        return AnalyticsReportOutput(
            total_sales=f"{total_sales_cents / 100:.2f}",
            orders_count=orders_count,
            carts_count=carts_count,
            customers_count=customers_count,
            favorites_count=favorites_count,
            reviews_count=reviews_count,
            average_ticket=f"{avg_ticket / 100:.2f}",
            conversion_rate=f"{conversion:.2f}",
        )
