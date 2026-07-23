from fastapi import APIRouter, Depends

from app.api.deps import get_login_user, get_refresh_token, get_register_user
from app.application.commands.auth import LoginUserUseCase, RefreshTokenUseCase, RegisterUserUseCase
from app.application.dto.schemas import LoginUserInput, RefreshTokenInput, RegisterUserInput, TokenOutput, UserOutput

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOutput, status_code=201)
async def register(data: RegisterUserInput, use_case: RegisterUserUseCase = Depends(get_register_user)):
    return await use_case.execute(data)


@router.post("/login", response_model=TokenOutput)
async def login(data: LoginUserInput, use_case: LoginUserUseCase = Depends(get_login_user)):
    return await use_case.execute(str(data.email), data.password)


@router.post("/refresh", response_model=TokenOutput)
async def refresh(data: RefreshTokenInput, use_case: RefreshTokenUseCase = Depends(get_refresh_token)):
    return await use_case.execute(data.refresh_token)
