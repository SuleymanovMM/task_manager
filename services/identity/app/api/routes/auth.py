from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service, get_current_user_id
from app.application.commands.change_password import ChangePasswordCommand, handle as handle_change_password
from app.application.commands.login import LoginCommand, handle as handle_login
from app.application.commands.logout import LogoutCommand, handle as handle_logout
from app.application.commands.logout_all import LogoutAllCommand, handle as handle_logout_all
from app.application.commands.refresh import RefreshTokenCommand, handle as handle_refresh
from app.application.commands.register import RegisterUserCommand, handle as handle_register
from app.application.queries.get_user import GetUserByIdQuery, handle as handle_get_user
from app.application.services.auth_service import AuthService
from app.core.rate_limit import RateLimiter
from app.schemas.requests import ChangePasswordRequest, LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest
from app.schemas.responses import TokenResponse, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

register_rate_limit = RateLimiter("register", limit=5, window_seconds=3600)
login_rate_limit = RateLimiter("login", limit=10, window_seconds=300)
refresh_rate_limit = RateLimiter("refresh", limit=30, window_seconds=60)
password_change_rate_limit = RateLimiter("password_change", limit=5, window_seconds=300)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(register_rate_limit.by_ip)]
)
async def register(request: RegisterRequest, auth: Annotated[AuthService, Depends(get_auth_service)]):
    result = await handle_register(
        RegisterUserCommand(
            email=str(request.email), username=request.username,
            password=request.password.get_secret_value(),
            first_name=request.first_name, last_name=request.last_name,
            avatar_url=request.avatar_url
        ), auth
    )
    await auth.user_repo.session.commit()
    return UserResponse.model_validate(result, from_attributes=True)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(login_rate_limit.by_ip)])
async def login(request: LoginRequest, auth: Annotated[AuthService, Depends(get_auth_service)]):
    result = await handle_login(LoginCommand(request.login, request.password.get_secret_value()), auth)
    await auth.user_repo.session.commit()
    return TokenResponse.model_validate(result, from_attributes=True)


@router.post("/token", response_model=TokenResponse, dependencies=[Depends(login_rate_limit.by_ip)])
async def token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth: Annotated[AuthService, Depends(get_auth_service)]
):
    """Form-логин для кнопки Authorize в Swagger — та же логика, что и /login."""
    result = await handle_login(LoginCommand(form_data.username, form_data.password), auth)
    await auth.user_repo.session.commit()
    return TokenResponse.model_validate(result, from_attributes=True)


@router.post("/refresh", response_model=TokenResponse, dependencies=[Depends(refresh_rate_limit.by_ip)])
async def refresh(request: RefreshRequest, auth: Annotated[AuthService, Depends(get_auth_service)]):
    result = await handle_refresh(RefreshTokenCommand(request.refresh_token), auth)
    await auth.user_repo.session.commit()
    return TokenResponse.model_validate(result, from_attributes=True)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: LogoutRequest, auth: Annotated[AuthService, Depends(get_auth_service)]):
    await handle_logout(LogoutCommand(request.refresh_token), auth)
    await auth.user_repo.session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
        user_id: Annotated[UUID, Depends(get_current_user_id)],
        auth: Annotated[AuthService, Depends(get_auth_service)]
):
    await handle_logout_all(LogoutAllCommand(user_id), auth)
    await auth.user_repo.session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/password/change", status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(password_change_rate_limit.by_user)]
)
async def change_password(
        request: ChangePasswordRequest,
        user_id: Annotated[UUID, Depends(get_current_user_id)],
        auth: Annotated[AuthService, Depends(get_auth_service)]
):
    await handle_change_password(
        ChangePasswordCommand(
            user_id, request.current_password.get_secret_value(), request.new_password.get_secret_value()
        ), auth
    )
    await auth.user_repo.session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
async def me(
        user_id: Annotated[UUID, Depends(get_current_user_id)],
        auth: Annotated[AuthService, Depends(get_auth_service)]
):
    result = await handle_get_user(GetUserByIdQuery(user_id), auth)
    return UserResponse.model_validate(result, from_attributes=True)
