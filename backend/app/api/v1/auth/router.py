from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import uuid4

from app.api.deps import get_login_user, get_refresh_token, get_register_user, get_uow
from app.application.commands.auth import LoginUserUseCase, RefreshTokenUseCase, RegisterUserUseCase
from app.application.dto.schemas import LoginUserInput, RefreshTokenInput, RegisterUserInput, TokenOutput, UserOutput
from app.core.security.jwt import JWTTokenService
from app.domain.users.entities.user import User
from app.infra.providers.oauth_providers import GitHubOAuthProvider, GoogleOAuthProvider
from app.infra.services.unit_of_work import SqlAlchemyUnitOfWork

router = APIRouter(prefix="/auth", tags=["Auth"])
_token_service = JWTTokenService()
_oauth_providers = {
    "google": GoogleOAuthProvider(),
    "github": GitHubOAuthProvider(),
}


@router.get("/oauth/{provider}/authorize")
async def oauth_authorize(provider: str) -> dict:
    if provider not in _oauth_providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    state = uuid4().hex
    url = _oauth_providers[provider].get_authorization_url(state=state)
    return {"authorization_url": url, "state": state}


@router.get("/oauth/callback", response_model=TokenOutput)
async def oauth_callback(
    provider: str = Query(...),
    code: str = Query(...),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    if provider not in _oauth_providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    oauth = _oauth_providers[provider]
    user_info = await oauth.exchange_code(code)
    user = await uow.users.find_by_email(user_info.email)
    if user is None:
        from app.core.security.password import Argon2PasswordHasher
        user = User.create(
            email=user_info.email,
            full_name=user_info.name or user_info.email,
            password_hash=Argon2PasswordHasher().hash(uuid4().hex),
        )
        await uow.users.save(user)
        await uow.commit()
    tokens = _token_service.create_tokens(user.id.value, [r.name for r in user.roles])
    return TokenOutput(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )


@router.post("/register", response_model=UserOutput, status_code=201)
async def register(data: RegisterUserInput, use_case: RegisterUserUseCase = Depends(get_register_user)):
    return await use_case.execute(data)


@router.post("/login", response_model=TokenOutput)
async def login(data: LoginUserInput, use_case: LoginUserUseCase = Depends(get_login_user)):
    return await use_case.execute(str(data.email), data.password)


@router.post("/refresh", response_model=TokenOutput)
async def refresh(data: RefreshTokenInput, use_case: RefreshTokenUseCase = Depends(get_refresh_token)):
    return await use_case.execute(data.refresh_token)
