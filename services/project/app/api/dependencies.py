from functools import lru_cache
from typing import Annotated, Callable
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import JWTService, CurrentUser
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories.sqlalchemy_project_repository import SQLAlchemyProjectRepository
from app.infrastructure.database.repositories.sqlalchemy_team_repository import SQLAlchemyTeamRepository
from app.infrastructure.database.repositories.sqlalchemy_invitation_repository import SQLAlchemyInvitationRepository
from app.infrastructure.messaging.publisher import publisher
from app.application.services.project_service import ProjectService
from app.application.services.team_service import TeamService
from app.domain.enums.project_role import ProjectRole
from app.domain.exceptions.project_exceptions import ProjectNotFoundError, ProjectAccessDeniedError


@lru_cache
def get_jwt_service() -> JWTService:
    return JWTService.from_file(settings.jwt_public_key_path, settings.jwt_algorithm)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


async def get_current_user(
        token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> CurrentUser:
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token", headers={"WWW-Authenticate": "Bearer"})
    try:
        return get_jwt_service().decode(token)
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired", headers={"WWW-Authenticate": "Bearer"}) from exc
    except (InvalidTokenError, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"}) from exc


SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


def get_project_service(db: SessionDep) -> ProjectService:
    return ProjectService(
        SQLAlchemyProjectRepository(db), SQLAlchemyTeamRepository(db), SQLAlchemyInvitationRepository(db), publisher
    )


def get_team_service(db: SessionDep) -> TeamService:
    return TeamService(SQLAlchemyTeamRepository(db))


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
TeamServiceDep = Annotated[TeamService, Depends(get_team_service)]


def require_project_role(*allowed_roles: ProjectRole) -> Callable:
    async def dependency(project_id: UUID, user: CurrentUserDep, db: SessionDep) -> CurrentUser:
        repo = SQLAlchemyProjectRepository(db)
        project = await repo.get(project_id)
        if project is None:
            raise ProjectNotFoundError()
        member = await repo.get_member(project_id, user.id)
        if member is None or member.role not in allowed_roles:
            raise ProjectAccessDeniedError()
        return user
    return dependency
