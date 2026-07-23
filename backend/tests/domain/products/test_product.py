import pytest

from app.domain.shared.entity_id import EntityId
from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.money import Money
from app.domain.products.entities.product import Product, ProductDimensions
from app.domain.products.entities.product_image import ProductImage
from app.domain.products.entities.product_variation import ProductVariation
from app.domain.products.enums.product_status import ProductStatus
from app.domain.products.events.product_events import ProductPublishedEvent


class TestProduct:
    @pytest.fixture
    def category_id(self) -> EntityId:
        return EntityId.generate()

    def test_create_as_draft(self, category_id: EntityId) -> None:
        product = Product.create(
            name="Camiseta Básica",
            description="Camiseta 100% algodão",
            sku="CAM-001",
            base_price=Money.from_decimal("49.90"),
            category_id=category_id,
        )
        assert product.status == ProductStatus.DRAFT
        assert product.slug.value == "camiseta-basica"

    def test_publish_requires_image_and_price(self, category_id: EntityId) -> None:
        product = Product.create(
            name="Camiseta",
            description="Descrição",
            sku="CAM-002",
            base_price=Money.from_decimal("0.00"),
            category_id=category_id,
        )
        with pytest.raises(DomainError):
            product.publish()

        product.update_price(Money.from_decimal("29.90"))
        with pytest.raises(DomainError):
            product.publish()

        product.add_image(ProductImage.create(storage_key="products/cam-002.jpg", is_primary=True))
        product.publish()
        assert product.status == ProductStatus.ACTIVE
        events = product.collect_events()
        assert any(isinstance(e, ProductPublishedEvent) for e in events)

    def test_add_variation_with_unique_sku(self, category_id: EntityId) -> None:
        product = Product.create(
            name="Tênis",
            description="Tênis esportivo",
            sku="TEN-001",
            base_price=Money.from_decimal("199.90"),
            category_id=category_id,
            dimensions=ProductDimensions(weight_grams=500, height_cm=10, width_cm=30, length_cm=35),
        )
        variation = ProductVariation.create(
            sku="TEN-001-P",
            attributes={"size": "40", "color": "black"},
            price=Money.from_decimal("199.90"),
        )
        product.add_variation(variation)
        assert product.resolve_price(variation.sku).amount_cents == 19990
