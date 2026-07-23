from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.interfaces.ports import ProductRepository
from app.domain.products.enums.product_status import ProductStatus
from app.infra.mappers.mappers import product_to_domain, product_to_model
from app.infra.models.models import ProductImageModel, ProductModel, ProductVariationModel


class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, product) -> None:
        result = await self._session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.images), selectinload(ProductModel.variations))
            .where(ProductModel.id == product.id.value)
        )
        model = result.scalar_one_or_none()
        if model is None:
            model = product_to_model(product)
            self._session.add(model)
        else:
            product_to_model(product, model)

        existing_images = {str(i.id): i for i in model.images}
        model.images.clear()
        for image in product.images:
            img_model = existing_images.get(str(image.id.value))
            if img_model is None:
                img_model = ProductImageModel(id=image.id.value, product_id=product.id.value)
            img_model.storage_key = image.storage_key
            img_model.alt_text = image.alt_text
            img_model.sort_order = image.sort_order
            img_model.is_primary = image.is_primary
            img_model.created_at = image.created_at
            model.images.append(img_model)

        existing_variations = {str(v.id): v for v in model.variations}
        model.variations.clear()
        for variation in product.variations:
            var_model = existing_variations.get(str(variation.id.value))
            if var_model is None:
                var_model = ProductVariationModel(id=variation.id.value, product_id=product.id.value)
            var_model.sku = str(variation.sku)
            var_model.attributes = variation.attributes
            var_model.price_cents = variation.price.amount_cents
            var_model.currency = variation.price.currency
            var_model.barcode = variation.barcode
            var_model.is_active = variation.is_active
            var_model.created_at = variation.created_at
            model.variations.append(var_model)

        await self._session.flush()

    async def find_by_id(self, product_id: UUID):
        result = await self._session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.images), selectinload(ProductModel.variations))
            .where(ProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()
        return product_to_domain(model) if model else None

    async def find_by_slug(self, slug: str):
        result = await self._session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.images), selectinload(ProductModel.variations))
            .where(ProductModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        return product_to_domain(model) if model else None

    async def list_active(self, *, offset: int = 0, limit: int = 20) -> list:
        result = await self._session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.images), selectinload(ProductModel.variations))
            .where(ProductModel.status == ProductStatus.ACTIVE.value)
            .offset(offset)
            .limit(limit)
        )
        return [product_to_domain(model) for model in result.scalars().all()]

    async def list_by_category(self, category_id: UUID, *, exclude_id: UUID | None = None, limit: int = 6) -> list:
        query = (
            select(ProductModel)
            .options(selectinload(ProductModel.images), selectinload(ProductModel.variations))
            .where(ProductModel.status == ProductStatus.ACTIVE.value, ProductModel.category_id == category_id)
        )
        if exclude_id:
            query = query.where(ProductModel.id != exclude_id)
        query = query.limit(limit)
        result = await self._session.execute(query)
        return [product_to_domain(model) for model in result.scalars().all()]
