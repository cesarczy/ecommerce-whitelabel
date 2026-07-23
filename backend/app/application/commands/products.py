from uuid import UUID

from app.application.dto.schemas import CreateProductInput, ProductOutput
from app.application.interfaces.ports import EventBus, UnitOfWork
from app.domain.products.entities.product import Product
from app.domain.products.entities.product_image import ProductImage
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.money import Money
from app.application.exceptions import NotFoundError


class CreateProductUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, data: CreateProductInput) -> ProductOutput:
        product = Product.create(
            name=data.name,
            description=data.description,
            sku=data.sku,
            base_price=Money.from_decimal(data.price),
            category_id=EntityId.from_string(data.category_id),
            brand_id=EntityId.from_string(data.brand_id) if data.brand_id else None,
            tags=data.tags,
        )
        await self._uow.products.save(product)
        events = product.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return _to_product_output(product)


class PublishProductUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, product_id: UUID, *, image_key: str) -> ProductOutput:
        product = await self._uow.products.find_by_id(product_id)
        if product is None:
            raise NotFoundError("Product not found")
        product.add_image(ProductImage.create(storage_key=image_key, is_primary=True))
        product.publish()
        await self._uow.products.save(product)
        events = product.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return _to_product_output(product)


class ListProductsUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, offset: int = 0, limit: int = 20) -> list[ProductOutput]:
        products = await self._uow.products.list_active(offset=offset, limit=limit)
        return [_to_product_output(product) for product in products]


def _to_product_output(product: Product) -> ProductOutput:
    primary = product.get_primary_image()
    return ProductOutput(
        id=str(product.id.value),
        name=str(product.name),
        slug=str(product.slug),
        description=product.description,
        sku=str(product.sku),
        price=str(product.base_price.to_decimal()),
        currency=product.base_price.currency,
        status=product.status.value,
        category_id=str(product.category_id.value),
        image_url=primary.storage_key if primary else None,
    )
