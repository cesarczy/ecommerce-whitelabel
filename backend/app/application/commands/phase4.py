from uuid import UUID

from app.application.commands.products import _to_product_output
from app.application.dto.schemas import (
    BannerOutput,
    CreateBannerInput,
    FavoriteOutput,
    ProductOutput,
    ProductVideoOutput,
    ResetPasswordInput,
    UpdateProductSeoInput,
    VerifyEmailInput,
)
from app.application.exceptions import ConflictError, NotFoundError
from app.application.interfaces.ports import EventBus, PasswordHasher, StoragePort, UnitOfWork
from app.core.context.tenant import get_current_tenant_id
from app.core.middlewares.tenant import DEFAULT_TENANT_ID
from app.domain.catalog.entities.favorite import Favorite
from app.domain.products.entities.product_video import ProductVideo
from app.domain.shared.entity_id import EntityId
from app.domain.store.entities.store_settings import Banner
from app.infra.notifications.email_notifier import queue_email
from app.infra.repositories.phase4_repositories import generate_secure_token, token_expiry


class AddFavoriteUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: UUID, product_id: UUID) -> FavoriteOutput:
        if await self._uow.favorites.exists(user_id, product_id):
            raise ConflictError("Product already in favorites")
        product = await self._uow.products.find_by_id(product_id)
        if product is None:
            raise NotFoundError("Product not found")
        favorite = Favorite.create(
            user_id=EntityId.from_string(str(user_id)),
            product_id=EntityId.from_string(str(product_id)),
        )
        await self._uow.favorites.add(favorite)
        await self._uow.commit()
        return FavoriteOutput(id=str(favorite.id.value), product_id=str(product_id))


class RemoveFavoriteUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: UUID, product_id: UUID) -> dict:
        await self._uow.favorites.remove(user_id, product_id)
        await self._uow.commit()
        return {"removed": True}


class ListFavoritesUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: UUID) -> list[ProductOutput]:
        favorites = await self._uow.favorites.list_by_user(user_id)
        products: list[ProductOutput] = []
        for fav in favorites:
            product = await self._uow.products.find_by_id(fav.product_id.value)
            if product and product.is_available():
                products.append(_to_product_output(product))
        return products


class UpdateProductSeoUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, product_id: UUID, data: UpdateProductSeoInput) -> ProductOutput:
        product = await self._uow.products.find_by_id(product_id)
        if product is None:
            raise NotFoundError("Product not found")
        product.update_details(
            seo_title=data.seo_title,
            seo_description=data.seo_description,
        )
        await self._uow.products.save(product)
        events = product.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        output = _to_product_output(product)
        return ProductOutput(
            **output.model_dump(),
            seo_title=product.seo_title,
            seo_description=product.seo_description,
        )


class GetRelatedProductsUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, product_id: UUID) -> list[ProductOutput]:
        product = await self._uow.products.find_by_id(product_id)
        if product is None:
            raise NotFoundError("Product not found")
        related = await self._uow.products.list_by_category(
            product.category_id.value,
            exclude_id=product_id,
            limit=6,
        )
        return [_to_product_output(p) for p in related]


class GetProductBySlugUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, slug: str) -> ProductOutput:
        product = await self._uow.products.find_by_slug(slug)
        if product is None or not product.is_available():
            raise NotFoundError("Product not found")
        output = _to_product_output(product)
        return ProductOutput(
            **output.model_dump(),
            seo_title=product.seo_title,
            seo_description=product.seo_description,
        )


class CreateBannerUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: CreateBannerInput) -> BannerOutput:
        banner = Banner.create(
            title=data.title,
            image_key=data.image_key,
            link_url=data.link_url,
            sort_order=data.sort_order,
        )
        await self._uow.banners.save(banner)
        await self._uow.commit()
        return BannerOutput(
            id=str(banner.id.value),
            title=banner.title,
            image_url=banner.image_key,
            link_url=banner.link_url,
            sort_order=banner.sort_order,
        )


class DeleteBannerUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, banner_id: UUID) -> dict:
        banner = await self._uow.banners.find_by_id(banner_id)
        if banner is None:
            raise NotFoundError("Banner not found")
        await self._uow.banners.delete(banner_id)
        await self._uow.commit()
        return {"deleted": True}


class ListBannersWithUrlsUseCase:
    def __init__(self, uow: UnitOfWork, storage: StoragePort) -> None:
        self._uow = uow
        self._storage = storage

    async def execute(self) -> list[BannerOutput]:
        tenant_id = get_current_tenant_id() or DEFAULT_TENANT_ID
        banners = await self._uow.banners.list_active(tenant_id)
        result: list[BannerOutput] = []
        for banner in banners:
            url = await self._storage.get_presigned_url(key=banner.image_key)
            result.append(
                BannerOutput(
                    id=str(banner.id.value),
                    title=banner.title,
                    image_url=url,
                    link_url=banner.link_url,
                    sort_order=banner.sort_order,
                )
            )
        return result


class AddProductVideoUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, product_id: UUID, *, storage_key: str, title: str = "") -> ProductVideoOutput:
        product = await self._uow.products.find_by_id(product_id)
        if product is None:
            raise NotFoundError("Product not found")
        video = ProductVideo.create(
            product_id=EntityId.from_string(str(product_id)),
            storage_key=storage_key,
            title=title,
        )
        await self._uow.product_videos.save(video)
        await self._uow.commit()
        return ProductVideoOutput(
            id=str(video.id.value),
            product_id=str(product_id),
            storage_key=video.storage_key,
            title=video.title,
        )


class ListProductVideosUseCase:
    def __init__(self, uow: UnitOfWork, storage: StoragePort) -> None:
        self._uow = uow
        self._storage = storage

    async def execute(self, product_id: UUID) -> list[ProductVideoOutput]:
        videos = await self._uow.product_videos.list_by_product(product_id)
        result: list[ProductVideoOutput] = []
        for video in videos:
            url = await self._storage.get_presigned_url(key=video.storage_key)
            result.append(
                ProductVideoOutput(
                    id=str(video.id.value),
                    product_id=str(product_id),
                    storage_key=url,
                    title=video.title,
                )
            )
        return result


class RequestPasswordResetUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, email: str) -> dict:
        user = await self._uow.users.find_by_email(email)
        if user is None:
            return {"message": "If the email exists, a reset link was sent"}
        token = generate_secure_token()
        await self._uow.user_tokens.create(
            user_id=user.id.value,
            token=token,
            token_type="password_reset",
            expires_at=token_expiry(hours=2),
        )
        await self._uow.commit()
        queue_email(
            to=str(user.email),
            subject="Redefinição de senha",
            body=f"Use o token: {token} em POST /api/v1/auth/reset-password",
        )
        return {"message": "If the email exists, a reset link was sent"}


class ResetPasswordUseCase:
    def __init__(self, uow: UnitOfWork, password_hasher: PasswordHasher) -> None:
        self._uow = uow
        self._password_hasher = password_hasher

    async def execute(self, data: ResetPasswordInput) -> dict:
        user_id = await self._uow.user_tokens.find_user_by_token(data.token, "password_reset")
        if user_id is None:
            raise NotFoundError("Invalid or expired token")
        user = await self._uow.users.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        user.change_password(self._password_hasher.hash(data.new_password))
        await self._uow.users.save(user)
        await self._uow.user_tokens.invalidate(data.token)
        await self._uow.commit()
        return {"password_reset": True}


class RequestEmailVerificationUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: UUID) -> dict:
        user = await self._uow.users.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        if user.email_verified:
            return {"message": "Email already verified"}
        token = generate_secure_token()
        await self._uow.user_tokens.create(
            user_id=user.id.value,
            token=token,
            token_type="email_verification",
            expires_at=token_expiry(hours=48),
        )
        await self._uow.commit()
        queue_email(
            to=str(user.email),
            subject="Confirme seu e-mail",
            body=f"Use o token: {token} em POST /api/v1/auth/verify-email",
        )
        return {"message": "Verification email sent"}


class VerifyEmailUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, data: VerifyEmailInput) -> dict:
        user_id = await self._uow.user_tokens.find_user_by_token(data.token, "email_verification")
        if user_id is None:
            raise NotFoundError("Invalid or expired token")
        user = await self._uow.users.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        user.verify_email()
        await self._uow.users.save(user)
        await self._uow.user_tokens.invalidate(data.token)
        events = user.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return {"email_verified": True}
