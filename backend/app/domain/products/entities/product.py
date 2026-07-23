from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.money import Money
from app.domain.shared.value_objects.sku import SKU
from app.domain.products.entities.product_image import ProductImage
from app.domain.products.entities.product_variation import ProductVariation
from app.domain.products.enums.product_status import ProductStatus
from app.domain.products.events.product_events import (
    ProductCreatedEvent,
    ProductDeactivatedEvent,
    ProductPriceChangedEvent,
    ProductPublishedEvent,
)
from app.domain.products.value_objects.product_name import ProductName
from app.domain.products.value_objects.slug import Slug


@dataclass
class ProductDimensions:
    weight_grams: int
    height_cm: int
    width_cm: int
    length_cm: int

    def __post_init__(self) -> None:
        if any(v <= 0 for v in (self.weight_grams, self.height_cm, self.width_cm, self.length_cm)):
            raise DomainError("Dimensions must be positive", code="INVALID_PRODUCT")


@dataclass
class Product(AggregateRoot):
    id: EntityId
    name: ProductName
    slug: Slug
    description: str
    sku: SKU
    barcode: str | None
    base_price: Money
    category_id: EntityId
    brand_id: EntityId | None
    status: ProductStatus
    tags: list[str]
    seo_title: str | None
    seo_description: str | None
    dimensions: ProductDimensions | None
    variations: list[ProductVariation]
    images: list[ProductImage]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        super().__init__()

    @classmethod
    def create(
        cls,
        *,
        name: str | ProductName,
        description: str,
        sku: str | SKU,
        base_price: Money,
        category_id: EntityId,
        brand_id: EntityId | None = None,
        barcode: str | None = None,
        tags: list[str] | None = None,
        slug: str | Slug | None = None,
        dimensions: ProductDimensions | None = None,
    ) -> Product:
        name_vo = name if isinstance(name, ProductName) else ProductName.create(name)
        sku_vo = sku if isinstance(sku, SKU) else SKU.create(sku)
        if slug is None:
            slug_vo = Slug.from_name(str(name_vo))
        elif isinstance(slug, Slug):
            slug_vo = slug
        else:
            slug_vo = Slug.create(slug)

        now = datetime.now(UTC)
        product = cls(
            id=EntityId.generate(),
            name=name_vo,
            slug=slug_vo,
            description=description.strip(),
            sku=sku_vo,
            barcode=barcode.strip() if barcode else None,
            base_price=base_price,
            category_id=category_id,
            brand_id=brand_id,
            status=ProductStatus.DRAFT,
            tags=sorted(set(tag.strip().lower() for tag in (tags or []) if tag.strip())),
            seo_title=None,
            seo_description=None,
            dimensions=dimensions,
            variations=[],
            images=[],
            created_at=now,
            updated_at=now,
        )
        product._record_event(
            ProductCreatedEvent(
                aggregate_id=product.id.value,
                name=str(name_vo),
                sku=str(sku_vo),
                category_id=str(category_id.value),
            )
        )
        return product

    @classmethod
    def reconstitute(
        cls,
        *,
        product_id: EntityId,
        name: ProductName,
        slug: Slug,
        description: str,
        sku: SKU,
        barcode: str | None,
        base_price: Money,
        category_id: EntityId,
        brand_id: EntityId | None,
        status: ProductStatus,
        tags: list[str],
        seo_title: str | None,
        seo_description: str | None,
        dimensions: ProductDimensions | None,
        variations: list[ProductVariation],
        images: list[ProductImage],
        created_at: datetime,
        updated_at: datetime,
    ) -> Product:
        return cls(
            id=product_id,
            name=name,
            slug=slug,
            description=description,
            sku=sku,
            barcode=barcode,
            base_price=base_price,
            category_id=category_id,
            brand_id=brand_id,
            status=status,
            tags=tags,
            seo_title=seo_title,
            seo_description=seo_description,
            dimensions=dimensions,
            variations=variations,
            images=images,
            created_at=created_at,
            updated_at=updated_at,
        )

    def update_details(
        self,
        *,
        name: str | ProductName | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        seo_title: str | None = None,
        seo_description: str | None = None,
    ) -> None:
        if name is not None:
            self.name = name if isinstance(name, ProductName) else ProductName.create(name)
        if description is not None:
            self.description = description.strip()
        if tags is not None:
            self.tags = sorted(set(tag.strip().lower() for tag in tags if tag.strip()))
        if seo_title is not None:
            self.seo_title = seo_title.strip() or None
        if seo_description is not None:
            self.seo_description = seo_description.strip() or None
        self.updated_at = datetime.now(UTC)

    def update_price(self, new_price: Money) -> None:
        if new_price.equals(self.base_price):
            return
        old = self.base_price
        self.base_price = new_price
        self.updated_at = datetime.now(UTC)
        self._record_event(
            ProductPriceChangedEvent(
                aggregate_id=self.id.value,
                old_price_cents=old.amount_cents,
                new_price_cents=new_price.amount_cents,
                currency=new_price.currency,
            )
        )

    def add_variation(self, variation: ProductVariation) -> None:
        if any(v.sku.value == variation.sku.value for v in self.variations):
            raise DomainError(f"SKU already exists: {variation.sku}", code="DUPLICATE_SKU")
        self.variations.append(variation)
        self.updated_at = datetime.now(UTC)

    def add_image(self, image: ProductImage) -> None:
        if image.is_primary:
            for existing in self.images:
                existing.is_primary = False
        elif not self.images:
            image.is_primary = True
        self.images.append(image)
        self.images.sort(key=lambda img: img.sort_order)
        self.updated_at = datetime.now(UTC)

    def remove_image(self, image_id: EntityId) -> None:
        before = len(self.images)
        self.images = [img for img in self.images if img.id.value != image_id.value]
        if len(self.images) == before:
            raise DomainError("Image not found", code="IMAGE_NOT_FOUND")
        if self.images and not any(img.is_primary for img in self.images):
            self.images[0].is_primary = True
        self.updated_at = datetime.now(UTC)

    def publish(self) -> None:
        if self.status == ProductStatus.ACTIVE:
            return
        if not self.images:
            raise DomainError("Product must have at least one image to publish", code="INVALID_PRODUCT")
        if self.base_price.amount_cents <= 0:
            raise DomainError("Product price must be greater than zero", code="INVALID_PRODUCT")
        if not self.description:
            raise DomainError("Product description is required to publish", code="INVALID_PRODUCT")
        self.status = ProductStatus.ACTIVE
        self.updated_at = datetime.now(UTC)
        self._record_event(
            ProductPublishedEvent(
                aggregate_id=self.id.value,
                name=str(self.name),
                slug=str(self.slug),
            )
        )

    def deactivate(self, reason: str | None = None) -> None:
        if self.status == ProductStatus.INACTIVE:
            return
        self.status = ProductStatus.INACTIVE
        self.updated_at = datetime.now(UTC)
        self._record_event(ProductDeactivatedEvent(aggregate_id=self.id.value, reason=reason))

    def get_primary_image(self) -> ProductImage | None:
        for image in self.images:
            if image.is_primary:
                return image
        return self.images[0] if self.images else None

    def resolve_price(self, sku: SKU | None = None) -> Money:
        if sku is None:
            return self.base_price
        for variation in self.variations:
            if variation.sku.value == sku.value and variation.is_active:
                return variation.price
        raise DomainError(f"Variation not found for SKU: {sku}", code="VARIATION_NOT_FOUND")

    def is_available(self) -> bool:
        return self.status == ProductStatus.ACTIVE
