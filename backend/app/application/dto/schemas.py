from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from app.domain.shared.exceptions import DomainError
from app.domain.shared.value_objects.email import Email


def _validate_app_email(value: str) -> str:
    try:
        return str(Email.create(value))
    except DomainError as exc:
        raise ValueError(str(exc)) from exc


AppEmail = Annotated[str, BeforeValidator(_validate_app_email)]


class RegisterUserInput(BaseModel):
    email: AppEmail
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = None


class LoginUserInput(BaseModel):
    email: AppEmail
    password: str


class RefreshTokenInput(BaseModel):
    refresh_token: str


class TokenOutput(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserOutput(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str | None
    email_verified: bool
    roles: list[str]


class AddressInput(BaseModel):
    street: str
    number: str
    complement: str | None = None
    neighborhood: str
    city: str
    state: str = Field(min_length=2, max_length=2)
    cep: str
    label: str = "Principal"
    is_default: bool = False


class CreateProductInput(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: str
    sku: str
    price: str
    category_id: str
    brand_id: str | None = None
    tags: list[str] = Field(default_factory=list)


class CategoryOutput(BaseModel):
    id: str
    name: str
    slug: str


class ProductOutput(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    sku: str
    price: str
    currency: str
    status: str
    category_id: str
    image_url: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None


class AddToCartInput(BaseModel):
    product_id: str
    sku: str
    quantity: int = Field(ge=1, le=99)
    session_id: str | None = None


class CartItemOutput(BaseModel):
    id: str
    product_id: str
    sku: str
    product_name: str
    unit_price: str
    quantity: int
    line_total: str


class CartOutput(BaseModel):
    id: str
    items: list[CartItemOutput]
    subtotal: str
    item_count: int


class CheckoutInput(BaseModel):
    cart_id: str
    shipping_address: AddressInput
    shipping_cost: str = "0.00"
    coupon_code: str | None = None


class OrderOutput(BaseModel):
    id: str
    order_number: str
    status: str
    subtotal: str
    discount: str
    shipping_cost: str
    total: str
    items: list[CartItemOutput]


class CouponOutput(BaseModel):
    id: str
    code: str
    discount_type: str
    discount_value: int
    is_active: bool


class CreateCouponInput(BaseModel):
    code: str = Field(min_length=3, max_length=30)
    discount_type: str = Field(pattern="^(percent|fixed)$")
    discount_value: int = Field(ge=1)
    min_order_amount: str = "0.00"
    max_uses: int | None = None


class UpdateInventoryInput(BaseModel):
    product_id: str
    sku: str
    quantity: int = Field(ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)


class CreatePaymentInput(BaseModel):
    order_id: str
    method: str = Field(pattern="^(pix|credit_card|boleto)$")
    provider: str = Field(default="mock", pattern="^(mock|mercado_pago|stripe)$")


class PaymentOutput(BaseModel):
    id: str
    order_id: str
    status: str
    provider: str
    method: str
    amount: str
    checkout_url: str | None = None


class DashboardReportOutput(BaseModel):
    total_sales: str
    orders_count: int
    customers_count: int
    low_stock_count: int
    average_ticket: str
    conversion_rate: str


class MfaEnrollOutput(BaseModel):
    secret: str
    provisioning_uri: str


class MfaVerifyInput(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class CreateReviewInput(BaseModel):
    product_id: str
    rating: int = Field(ge=1, le=5)
    title: str = Field(default="", max_length=200)
    comment: str = Field(min_length=3, max_length=2000)
    order_id: str | None = None


class ReviewOutput(BaseModel):
    id: str
    product_id: str
    rating: int
    title: str
    comment: str


class StoreSettingsOutput(BaseModel):
    name: str
    tagline: str
    logo_url: str | None
    primary_color: str
    secondary_color: str


class UpdateStoreInput(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    tagline: str | None = Field(default=None, max_length=300)
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None


class PaymentWebhookInput(BaseModel):
    external_id: str
    status: str


class BannerOutput(BaseModel):
    id: str
    title: str
    image_url: str
    link_url: str | None
    sort_order: int


class CreateBannerInput(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    image_key: str = Field(min_length=3, max_length=500)
    link_url: str | None = None
    sort_order: int = 0


class FavoriteOutput(BaseModel):
    id: str
    product_id: str


class UpdateProductSeoInput(BaseModel):
    seo_title: str | None = Field(default=None, max_length=200)
    seo_description: str | None = Field(default=None, max_length=300)


class ProductVideoOutput(BaseModel):
    id: str
    product_id: str
    storage_key: str
    title: str


class ForgotPasswordInput(BaseModel):
    email: AppEmail


class ResetPasswordInput(BaseModel):
    token: str = Field(min_length=20)
    new_password: str = Field(min_length=8, max_length=128)


class VerifyEmailInput(BaseModel):
    token: str = Field(min_length=20)


class AnalyticsReportOutput(BaseModel):
    total_sales: str
    orders_count: int
    carts_count: int
    customers_count: int
    favorites_count: int
    reviews_count: int
    average_ticket: str
    conversion_rate: str
