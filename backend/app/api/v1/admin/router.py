from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
async def dashboard() -> dict:
    return {
        "total_sales": "0.00",
        "orders_count": 0,
        "low_stock_count": 0,
        "customers_count": 0,
    }
