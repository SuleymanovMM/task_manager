from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Response
from app.api.dependencies import CurrentUserDep, ProjectServiceDep, SessionDep, require_project_role
from app.core.security import CurrentUser
from app.domain.enums.project_role import ProjectRole
from app.schemas.requests import ProjectCreateRequest, ProjectPatchRequest
from app.schemas.responses import ProjectResponse, PaginatedProjects

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create(req: ProjectCreateRequest, user: CurrentUserDep, projects: ProjectServiceDep, db: SessionDep):
    result = await projects.create_project(user.id, req)
    await db.commit()
    return result


@router.get("", response_model=PaginatedProjects)
async def list_projects(user: CurrentUserDep, projects: ProjectServiceDep, offset: int = 0, limit: int = 20):
    limit = max(1, min(limit, 100))
    items, total = await projects.list_projects(user.id, offset, limit)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.get("/{project_id}", response_model=ProjectResponse)
async def get(project_id: UUID, user: CurrentUserDep, projects: ProjectServiceDep):
    return await projects.get_project(project_id, user.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def patch(
    project_id: UUID, req: ProjectPatchRequest,
    user: Annotated[CurrentUser, Depends(require_project_role(ProjectRole.OWNER))],
    projects: ProjectServiceDep, db: SessionDep,
):
    result = await projects.update_project(project_id, user.id, req)
    await db.commit()
    return result


@router.delete("/{project_id}", status_code=204)
async def delete(
    project_id: UUID, user: Annotated[CurrentUser, Depends(require_project_role(ProjectRole.OWNER))],
    projects: ProjectServiceDep, db: SessionDep,
):
    await projects.archive_project(project_id, user.id)
    await db.commit()
    return Response(status_code=204)
