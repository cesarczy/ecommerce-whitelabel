from fastapi import APIRouter, Depends

from app.api.deps import get_dashboard_query, get_analytics_query
from app.application.dto.schemas import AnalyticsReportOutput, DashboardReportOutput
from app.application.queries.analytics import GetAnalyticsReportQuery
from app.application.queries.dashboard import GetDashboardReportQuery

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardReportOutput)
async def dashboard(query: GetDashboardReportQuery = Depends(get_dashboard_query)):
    return await query.execute()


@router.get("/analytics", response_model=AnalyticsReportOutput)
async def analytics(query: GetAnalyticsReportQuery = Depends(get_analytics_query)):
    return await query.execute()
