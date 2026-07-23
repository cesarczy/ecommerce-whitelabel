from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.schemas import DashboardReportOutput
from app.core.context.tenant import get_current_tenant_id
from app.core.middlewares.tenant import DEFAULT_TENANT_ID
from app.infra.models.models import InventoryModel, OrderModel, PaymentModel, UserModel


class GetDashboardReportQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self) -> DashboardReportOutput:
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

        customers_result = await self._session.execute(select(func.count(UserModel.id)))
        customers_count = int(customers_result.scalar_one())

        low_stock_result = await self._session.execute(
            select(func.count(InventoryModel.id)).where(
                InventoryModel.tenant_id == tenant_id,
                InventoryModel.quantity_available <= InventoryModel.low_stock_threshold,
            )
        )
        low_stock_count = int(low_stock_result.scalar_one())

        avg_ticket = total_sales_cents / orders_count if orders_count else 0

        return DashboardReportOutput(
            total_sales=f"{total_sales_cents / 100:.2f}",
            orders_count=orders_count,
            customers_count=customers_count,
            low_stock_count=low_stock_count,
            average_ticket=f"{avg_ticket / 100:.2f}",
            conversion_rate="0.00",
        )
