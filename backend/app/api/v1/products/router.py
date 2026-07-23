from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_create_product, get_list_products, get_publish_product, require_staff
from app.application.commands.products import CreateProductUseCase, ListProductsUseCase, PublishProductUseCase
from app.application.dto.schemas import CreateProductInput, ProductOutput

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductOutput])
async def list_products(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    use_case: ListProductsUseCase = Depends(get_list_products),
):
    return await use_case.execute(offset=offset, limit=limit)


@router.post("", response_model=ProductOutput, status_code=201, dependencies=[Depends(require_staff)])
async def create_product(
    data: CreateProductInput,
    use_case: CreateProductUseCase = Depends(get_create_product),
):
    return await use_case.execute(data)


@router.post("/{product_id}/publish", response_model=ProductOutput, dependencies=[Depends(require_staff)])
async def publish_product(
    product_id: UUID,
    image_key: str = Query(..., description="MinIO storage key"),
    use_case: PublishProductUseCase = Depends(get_publish_product),
):
    return await use_case.execute(product_id, image_key=image_key)
