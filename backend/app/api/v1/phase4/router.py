from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_add_favorite,
    get_add_product_video,
    get_banners_with_urls,
    get_create_banner,
    get_current_user_id,
    get_delete_banner,
    get_list_favorites,
    get_list_product_videos,
    get_product_by_slug,
    get_related_products,
    get_remove_favorite,
    get_update_product_seo,
)
from app.application.commands.phase4 import (
    AddFavoriteUseCase,
    AddProductVideoUseCase,
    CreateBannerUseCase,
    DeleteBannerUseCase,
    GetProductBySlugUseCase,
    GetRelatedProductsUseCase,
    ListBannersWithUrlsUseCase,
    ListFavoritesUseCase,
    ListProductVideosUseCase,
    RemoveFavoriteUseCase,
    UpdateProductSeoUseCase,
)
from app.application.dto.schemas import (
    BannerOutput,
    CreateBannerInput,
    FavoriteOutput,
    ProductOutput,
    ProductVideoOutput,
    UpdateProductSeoInput,
)

router = APIRouter(tags=["Phase 4"])


@router.post("/favorites/{product_id}", response_model=FavoriteOutput, status_code=201)
async def add_favorite(
    product_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    use_case: AddFavoriteUseCase = Depends(get_add_favorite),
):
    return await use_case.execute(user_id, product_id)


@router.delete("/favorites/{product_id}")
async def remove_favorite(
    product_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    use_case: RemoveFavoriteUseCase = Depends(get_remove_favorite),
):
    return await use_case.execute(user_id, product_id)


@router.get("/favorites", response_model=list[ProductOutput])
async def list_favorites(
    user_id: UUID = Depends(get_current_user_id),
    use_case: ListFavoritesUseCase = Depends(get_list_favorites),
):
    return await use_case.execute(user_id)


@router.get("/products/slug/{slug}", response_model=ProductOutput)
async def get_product_by_slug(
    slug: str,
    use_case: GetProductBySlugUseCase = Depends(get_product_by_slug),
):
    return await use_case.execute(slug)


@router.get("/products/{product_id}/related", response_model=list[ProductOutput])
async def related_products(
    product_id: UUID,
    use_case: GetRelatedProductsUseCase = Depends(get_related_products),
):
    return await use_case.execute(product_id)


@router.put("/products/{product_id}/seo", response_model=ProductOutput)
async def update_product_seo(
    product_id: UUID,
    data: UpdateProductSeoInput,
    _user_id: UUID = Depends(get_current_user_id),
    use_case: UpdateProductSeoUseCase = Depends(get_update_product_seo),
):
    return await use_case.execute(product_id, data)


@router.post("/admin/banners", response_model=BannerOutput, status_code=201)
async def create_banner(
    data: CreateBannerInput,
    _user_id: UUID = Depends(get_current_user_id),
    use_case: CreateBannerUseCase = Depends(get_create_banner),
):
    return await use_case.execute(data)


@router.delete("/admin/banners/{banner_id}")
async def delete_banner(
    banner_id: UUID,
    _user_id: UUID = Depends(get_current_user_id),
    use_case: DeleteBannerUseCase = Depends(get_delete_banner),
):
    return await use_case.execute(banner_id)


@router.get("/store/banners/presigned", response_model=list[BannerOutput])
async def list_banners_presigned(use_case: ListBannersWithUrlsUseCase = Depends(get_banners_with_urls)):
    return await use_case.execute()


@router.post("/products/{product_id}/videos", response_model=ProductVideoOutput, status_code=201)
async def add_product_video(
    product_id: UUID,
    storage_key: str = Query(...),
    title: str = Query(""),
    _user_id: UUID = Depends(get_current_user_id),
    use_case: AddProductVideoUseCase = Depends(get_add_product_video),
):
    return await use_case.execute(product_id, storage_key=storage_key, title=title)


@router.get("/products/{product_id}/videos", response_model=list[ProductVideoOutput])
async def list_product_videos(
    product_id: UUID,
    use_case: ListProductVideosUseCase = Depends(get_list_product_videos),
):
    return await use_case.execute(product_id)
