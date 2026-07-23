from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import (
    get_banners_query,
    get_create_review,
    get_current_user_id,
    get_list_orders,
    get_process_webhook,
    get_product_rating_query,
    get_product_reviews_query,
    get_store_query,
    get_update_store,
)
from app.application.commands.phase3 import (
    CreateReviewUseCase,
    ListCustomerOrdersUseCase,
    ProcessPaymentWebhookUseCase,
    UpdateStoreSettingsUseCase,
)
from app.application.dto.schemas import (
    BannerOutput,
    CreateReviewInput,
    OrderOutput,
    PaymentOutput,
    PaymentWebhookInput,
    ReviewOutput,
    StoreSettingsOutput,
    UpdateStoreInput,
)
from app.application.queries.store import (
    GetProductRatingQuery,
    GetStoreSettingsQuery,
    ListBannersQuery,
    ListProductReviewsQuery,
)

router = APIRouter(tags=["Phase 3"])


@router.post("/webhooks/payments/{provider}", response_model=PaymentOutput)
async def payment_webhook(
    provider: str,
    data: PaymentWebhookInput,
    use_case: ProcessPaymentWebhookUseCase = Depends(get_process_webhook),
):
    return await use_case.execute(provider=provider, external_id=data.external_id, status=data.status)


@router.get("/orders", response_model=list[OrderOutput])
async def list_my_orders(
    user_id: UUID = Depends(get_current_user_id),
    use_case: ListCustomerOrdersUseCase = Depends(get_list_orders),
):
    return await use_case.execute(user_id)


@router.post("/reviews", response_model=ReviewOutput, status_code=201)
async def create_review(
    data: CreateReviewInput,
    user_id: UUID = Depends(get_current_user_id),
    use_case: CreateReviewUseCase = Depends(get_create_review),
):
    return await use_case.execute(user_id, data)


@router.get("/products/{product_id}/reviews")
async def list_product_reviews(
    product_id: UUID,
    query: ListProductReviewsQuery = Depends(get_product_reviews_query),
):
    return await query.execute(product_id)


@router.get("/products/{product_id}/rating")
async def product_rating(
    product_id: UUID,
    query: GetProductRatingQuery = Depends(get_product_rating_query),
):
    return await query.execute(product_id)


@router.get("/store/settings", response_model=StoreSettingsOutput)
async def get_store_settings(query: GetStoreSettingsQuery = Depends(get_store_query)):
    return await query.execute()


@router.put("/store/settings", response_model=StoreSettingsOutput)
async def update_store_settings(
    data: UpdateStoreInput,
    _user_id: UUID = Depends(get_current_user_id),
    use_case: UpdateStoreSettingsUseCase = Depends(get_update_store),
):
    return await use_case.execute(data)


@router.get("/store/banners", response_model=list[BannerOutput])
async def list_banners(query: ListBannersQuery = Depends(get_banners_query)):
    return await query.execute()
