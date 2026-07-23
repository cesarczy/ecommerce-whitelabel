from uuid import UUID

from app.application.dto.schemas import AddressInput, UserOutput
from app.application.exceptions import NotFoundError
from app.application.interfaces.ports import EventBus, UnitOfWork
from app.domain.shared.entity_id import EntityId
from app.domain.shared.value_objects.address import Address


class GetUserProfileUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: UUID) -> UserOutput:
        from app.application.commands.auth import _to_user_output

        user = await self._uow.users.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return _to_user_output(user)


class AddUserAddressUseCase:
    def __init__(self, uow: UnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def execute(self, user_id: UUID, data: AddressInput) -> UserOutput:
        from app.application.commands.auth import _to_user_output

        user = await self._uow.users.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")

        address = Address.create(
            street=data.street,
            number=data.number,
            complement=data.complement,
            neighborhood=data.neighborhood,
            city=data.city,
            state=data.state,
            cep=data.cep,
            label=data.label,
        )
        user.add_address(address, is_default=data.is_default)
        await self._uow.users.save(user)
        events = user.collect_events()
        await self._uow.commit()
        await self._event_bus.publish(events)
        return _to_user_output(user)
