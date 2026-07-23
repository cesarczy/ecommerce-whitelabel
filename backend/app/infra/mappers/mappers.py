from app.domain.products.entities.product import Product, ProductDimensions
from app.domain.products.entities.product_image import ProductImage
from app.domain.products.entities.product_variation import ProductVariation
from app.domain.products.enums.product_status import ProductStatus
from app.domain.products.value_objects.product_name import ProductName
from app.domain.products.value_objects.slug import Slug
from app.domain.shared.entity_id import EntityId
from app.domain.shared.value_objects.money import Money
from app.domain.shared.value_objects.sku import SKU
from app.domain.users.entities.role import Role
from app.domain.users.entities.user import User
from app.domain.users.entities.user_address import UserAddress
from app.domain.users.enums.user_status import UserStatus
from app.domain.shared.value_objects.address import Address
from app.domain.shared.value_objects.email import Email
from app.domain.shared.value_objects.phone import Phone
from app.domain.orders.entities.cart import Cart
from app.domain.orders.entities.cart_item import CartItem
from app.domain.orders.entities.order import Order
from app.domain.orders.entities.order_item import OrderItem
from app.domain.orders.entities.order_status_history import OrderStatusHistory
from app.domain.orders.enums.order_status import OrderStatus
from app.domain.orders.value_objects.order_number import OrderNumber
from app.infra.models.models import (
    CartItemModel,
    CartModel,
    OrderItemModel,
    OrderModel,
    OrderStatusHistoryModel,
    ProductImageModel,
    ProductModel,
    ProductVariationModel,
    RoleModel,
    UserAddressModel,
    UserModel,
)


def user_to_domain(model: UserModel) -> User:
    roles = [
        Role.reconstitute(EntityId.from_string(str(r.id)), r.name, list(r.permissions or []))
        for r in model.roles
    ]
    addresses = [
        UserAddress.reconstitute(
            EntityId.from_string(str(a.id)),
            Address.create(
                street=a.street,
                number=a.number,
                complement=a.complement,
                neighborhood=a.neighborhood,
                city=a.city,
                state=a.state,
                cep=a.cep,
                label=a.label,
            ),
            a.is_default,
            a.created_at,
        )
        for a in model.addresses
    ]
    return User.reconstitute(
        user_id=EntityId.from_string(str(model.id)),
        email=Email.create(model.email),
        full_name=model.full_name,
        password_hash=model.password_hash,
        phone=Phone.create(model.phone) if model.phone else None,
        status=UserStatus(model.status),
        email_verified=model.email_verified,
        mfa_enabled=model.mfa_enabled,
        roles=roles,
        addresses=addresses,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def user_to_model(user: User, model: UserModel | None = None) -> UserModel:
    if model is None:
        model = UserModel(id=user.id.value)
    model.email = str(user.email)
    model.full_name = user.full_name
    model.password_hash = user.password_hash
    model.phone = str(user.phone) if user.phone else None
    model.status = user.status.value
    model.email_verified = user.email_verified
    model.mfa_enabled = user.mfa_enabled
    model.created_at = user.created_at
    model.updated_at = user.updated_at
    return model


def product_to_domain(model: ProductModel) -> Product:
    dimensions = None
    if model.weight_grams and model.height_cm and model.width_cm and model.length_cm:
        dimensions = ProductDimensions(
            weight_grams=model.weight_grams,
            height_cm=model.height_cm,
            width_cm=model.width_cm,
            length_cm=model.length_cm,
        )
    variations = [
        ProductVariation.reconstitute(
            EntityId.from_string(str(v.id)),
            SKU.create(v.sku),
            dict(v.attributes or {}),
            Money(v.price_cents, v.currency),
            v.barcode,
            v.is_active,
            v.created_at,
        )
        for v in model.variations
    ]
    images = [
        ProductImage.reconstitute(
            EntityId.from_string(str(i.id)),
            i.storage_key,
            i.alt_text,
            i.sort_order,
            i.is_primary,
            i.created_at,
        )
        for i in model.images
    ]
    return Product.reconstitute(
        product_id=EntityId.from_string(str(model.id)),
        name=ProductName.create(model.name),
        slug=Slug.create(model.slug),
        description=model.description,
        sku=SKU.create(model.sku),
        barcode=model.barcode,
        base_price=Money(model.price_cents, model.currency),
        category_id=EntityId.from_string(str(model.category_id)),
        brand_id=EntityId.from_string(str(model.brand_id)) if model.brand_id else None,
        status=ProductStatus(model.status),
        tags=list(model.tags or []),
        seo_title=model.seo_title,
        seo_description=model.seo_description,
        dimensions=dimensions,
        variations=variations,
        images=images,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def product_to_model(product: Product, model: ProductModel | None = None) -> ProductModel:
    if model is None:
        model = ProductModel(id=product.id.value)
    model.name = str(product.name)
    model.slug = str(product.slug)
    model.description = product.description
    model.sku = str(product.sku)
    model.barcode = product.barcode
    model.price_cents = product.base_price.amount_cents
    model.currency = product.base_price.currency
    model.category_id = product.category_id.value
    model.brand_id = product.brand_id.value if product.brand_id else None
    model.status = product.status.value
    model.tags = product.tags
    model.seo_title = product.seo_title
    model.seo_description = product.seo_description
    if product.dimensions:
        model.weight_grams = product.dimensions.weight_grams
        model.height_cm = product.dimensions.height_cm
        model.width_cm = product.dimensions.width_cm
        model.length_cm = product.dimensions.length_cm
    model.created_at = product.created_at
    model.updated_at = product.updated_at
    return model


def cart_to_domain(model: CartModel) -> Cart:
    items = [
        CartItem.reconstitute(
            EntityId.from_string(str(i.id)),
            EntityId.from_string(str(i.product_id)),
            SKU.create(i.sku),
            i.product_name,
            Money(i.unit_price_cents, i.currency),
            i.quantity,
            i.added_at,
        )
        for i in model.items
    ]
    return Cart.reconstitute(
        cart_id=EntityId.from_string(str(model.id)),
        customer_id=EntityId.from_string(str(model.customer_id)) if model.customer_id else None,
        session_id=model.session_id,
        items=items,
        coupon_code=model.coupon_code,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def order_to_domain(model: OrderModel) -> Order:
    items = [
        OrderItem.reconstitute(
            EntityId.from_string(str(i.id)),
            EntityId.from_string(str(i.product_id)),
            SKU.create(i.sku),
            i.product_name,
            Money(i.unit_price_cents, i.currency),
            i.quantity,
        )
        for i in model.items
    ]
    history = [
        OrderStatusHistory.reconstitute(OrderStatus(h.status), h.changed_at, h.note)
        for h in model.status_history
    ]
    shipping_address = Address.create(
        street=model.shipping_street,
        number=model.shipping_number,
        complement=model.shipping_complement,
        neighborhood=model.shipping_neighborhood,
        city=model.shipping_city,
        state=model.shipping_state,
        cep=model.shipping_cep,
    )
    order = Order.reconstitute(
        order_id=EntityId.from_string(str(model.id)),
        order_number=OrderNumber.create(model.order_number),
        customer_id=EntityId.from_string(str(model.customer_id)),
        items=items,
        shipping_address=shipping_address,
        status=OrderStatus(model.status),
        status_history=history,
        subtotal=Money(model.subtotal_cents, model.currency),
        discount=Money(model.discount_cents, model.currency),
        shipping_cost=Money(model.shipping_cost_cents, model.currency),
        total=Money(model.total_cents, model.currency),
        coupon_id=EntityId.from_string(str(model.coupon_id)) if model.coupon_id else None,
        payment_id=EntityId.from_string(str(model.payment_id)) if model.payment_id else None,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
    return order
