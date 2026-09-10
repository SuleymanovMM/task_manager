from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.auth_service import AuthService
from app.core.config import settings
from app.core.security import JWTService, PasswordService
from app.domain.enums.role import UserRole
from app.infrastructure.database.repositories.sqlalchemy_refresh_token_repository import \
    SQLAlchemyRefreshTokenRepository
from app.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.infrastructure.database.session import get_session

password_service = PasswordService()
# auto_error=False: свои 401/сообщения ниже, а не дефолтные от FastAPI. tokenUrl даёт
# Swagger форму логина в кнопке "Authorize" вместо просто поля под токен.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


@lru_cache
def get_jwt_service() -> JWTService:
    return JWTService.from_files(
        settings.jwt_private_key_path, settings.jwt_public_key_path, settings.jwt_algorithm, settings.app_name
    )


def get_auth_service(
        db: Annotated[AsyncSession, Depends(get_session)],
        jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> AuthService:
    return AuthService(
        user_repo=SQLAlchemyUserRepository(db),
        refresh_repo=SQLAlchemyRefreshTokenRepository(db),
        password_service=password_service,
        jwt_service=jwt_service,
        access_minutes=settings.access_token_expire_minutes,
        refresh_days=settings.refresh_token_expire_days,
    )


async def get_current_user_id(
        jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
        token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> UUID:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt_service.decode_access_token(token)
        return UUID(payload["sub"])
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired",
                            headers={"WWW-Authenticate": "Bearer"}) from exc
    except (InvalidTokenError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token",
                            headers={"WWW-Authenticate": "Bearer"}) from exc
