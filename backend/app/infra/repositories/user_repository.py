from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.application.interfaces.ports import UserRepository
from app.domain.users.entities.role import ADMIN_ROLE, CUSTOMER_ROLE, STAFF_ROLE, Role
from app.domain.users.entities.user import User
from app.infra.mappers.mappers import user_to_domain, user_to_model
from app.infra.models.models import RoleModel, UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> None:
        result = await self._session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles), selectinload(UserModel.addresses))
            .where(UserModel.id == user.id.value)
        )
        model = result.scalar_one_or_none()
        is_new = model is None
        if is_new:
            model = user_to_model(user)
        else:
            user_to_model(user, model)

        role_names = {role.name for role in user.roles}
        roles_result = await self._session.execute(select(RoleModel).where(RoleModel.name.in_(role_names)))
        model.roles = list(roles_result.scalars().all())

        existing_addresses: dict[str, object] = {}
        if not is_new:
            existing_addresses = {str(a.id): a for a in model.addresses}
            model.addresses.clear()

        for address in user.addresses:
            addr_model = existing_addresses.get(str(address.id.value))
            if addr_model is None:
                from app.infra.models.models import UserAddressModel

                addr_model = UserAddressModel(id=address.id.value, user_id=user.id.value)
            addr_model.street = address.address.street
            addr_model.number = address.address.number
            addr_model.complement = address.address.complement
            addr_model.neighborhood = address.address.neighborhood
            addr_model.city = address.address.city
            addr_model.state = address.address.state
            addr_model.cep = address.address.cep.value
            addr_model.label = address.address.label
            addr_model.is_default = address.is_default
            addr_model.created_at = address.created_at
            model.addresses.append(addr_model)

        if is_new:
            self._session.add(model)

        await self._session.flush()

    async def find_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles), selectinload(UserModel.addresses))
            .where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return user_to_domain(model) if model else None

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles), selectinload(UserModel.addresses))
            .where(UserModel.email == email.lower())
        )
        model = result.scalar_one_or_none()
        return user_to_domain(model) if model else None

    async def exists_by_email(self, email: str) -> bool:
        result = await self._session.execute(select(UserModel.id).where(UserModel.email == email.lower()))
        return result.scalar_one_or_none() is not None


async def seed_default_roles(session: AsyncSession) -> None:
    for role in (CUSTOMER_ROLE, ADMIN_ROLE, STAFF_ROLE):
        result = await session.execute(select(RoleModel).where(RoleModel.name == role.name))
        if result.scalar_one_or_none() is None:
            session.add(
                RoleModel(id=role.id.value, name=role.name, permissions=role.permissions)
            )


async def seed_default_admin(session: AsyncSession) -> None:
    from app.core.config.settings import settings
    from app.core.security.password import Argon2PasswordHasher

    if not settings.seed_admin_enabled:
        return

    email = settings.seed_admin_email.lower()
    result = await session.execute(select(UserModel.id).where(UserModel.email == email))
    if result.scalar_one_or_none() is not None:
        return

    user = User.create(
        email=email,
        full_name=settings.seed_admin_name,
        password_hash=Argon2PasswordHasher().hash(settings.seed_admin_password),
        roles=[ADMIN_ROLE],
    )
    user.verify_email()
    repo = SqlAlchemyUserRepository(session)
    await repo.save(user)
