from functools import lru_cache
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import JWTService
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories.sqlalchemy_notification_repository import SqlAlchemyNotificationRepository


@lru_cache
def get_jwt_service() -> JWTService:
    return JWTService(settings.jwt_public_key_path, settings.jwt_algorithm)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


async def get_current_user(
        token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> UUID:
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        payload = get_jwt_service().decode(token)
        return UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token") from None


async def get_notification_repo(db: Annotated[AsyncSession, Depends(get_db)]):
    return SqlAlchemyNotificationRepository(db)
