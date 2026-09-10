from functools import lru_cache
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import CurrentUser, JWTService
from app.infrastructure.database.session import get_db
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.external.project_client import ProjectClient
from app.application.services.task_service import TaskService


@lru_cache
def get_jwt_service() -> JWTService:
    return JWTService.from_file(settings.jwt_public_key_path, settings.jwt_algorithm)


@lru_cache
def get_cache() -> RedisCache:
    return RedisCache()


@lru_cache
def get_project_client() -> ProjectClient:
    return ProjectClient()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


async def get_auth(
        token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> tuple[CurrentUser, str]:
    if not token:
        raise HTTPException(401, "Missing bearer token", headers={"WWW-Authenticate": "Bearer"})
    try:
        return get_jwt_service().decode(token), token
    except ExpiredSignatureError:
        raise HTTPException(401, "Token expired", headers={"WWW-Authenticate": "Bearer"})
    except (InvalidTokenError, ValueError, KeyError, TypeError):
        raise HTTPException(401, "Invalid token", headers={"WWW-Authenticate": "Bearer"})


AuthDep = Annotated[tuple[CurrentUser, str], Depends(get_auth)]


def get_task_service(db: Annotated[AsyncSession, Depends(get_db)]) -> TaskService:
    return TaskService(db, get_cache(), get_project_client())


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
