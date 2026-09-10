from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.infrastructure.external.identity_client import IdentityUnavailableError, InvalidCredentialsError, \
    login_via_identity

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/token")
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Только для кнопки Authorize в Swagger: логинится через Identity и возвращает токен."""
    try:
        data = await login_via_identity(form_data.username, form_data.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password") from exc
    except IdentityUnavailableError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Identity Service unavailable") from exc
    return {"access_token": data["access_token"], "token_type": "bearer"}
