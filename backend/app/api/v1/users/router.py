from fastapi import APIRouter, Depends
from uuid import UUID

from app.api.deps import get_add_address, get_current_user_id, get_user_profile
from app.application.commands.users import AddUserAddressUseCase, GetUserProfileUseCase
from app.application.dto.schemas import AddressInput, UserOutput

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOutput)
async def me(
    user_id: UUID = Depends(get_current_user_id),
    use_case: GetUserProfileUseCase = Depends(get_user_profile),
):
    return await use_case.execute(user_id)


@router.post("/me/addresses", response_model=UserOutput)
async def add_address(
    data: AddressInput,
    user_id: UUID = Depends(get_current_user_id),
    use_case: AddUserAddressUseCase = Depends(get_add_address),
):
    return await use_case.execute(user_id, data)
