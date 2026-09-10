from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Response
from app.api.dependencies import CurrentUserDep, ProjectServiceDep, SessionDep, require_project_role
from app.core.security import CurrentUser
from app.domain.enums.project_role import ProjectRole
from app.schemas.requests import AddMemberRequest
from app.schemas.responses import MemberResponse

router = APIRouter(prefix="/api/v1/projects/{project_id}/members", tags=["members"])


@router.post("", response_model=MemberResponse, status_code=201)
async def add(
    project_id: UUID, req: AddMemberRequest,
    user: Annotated[CurrentUser, Depends(require_project_role(ProjectRole.OWNER, ProjectRole.MANAGER))],
    projects: ProjectServiceDep, db: SessionDep,
):
    member = await projects.add_member(project_id, user.id, req.user_id, req.role)
    await db.commit()
    return member


@router.get("", response_model=list[MemberResponse])
async def list_members(project_id: UUID, user: CurrentUserDep, projects: ProjectServiceDep):
    return await projects.members(project_id, user.id)


@router.delete("/{user_id}", status_code=204)
async def remove(
    project_id: UUID, user_id: UUID,
    user: Annotated[CurrentUser, Depends(require_project_role(ProjectRole.OWNER, ProjectRole.MANAGER))],
    projects: ProjectServiceDep, db: SessionDep,
):
    await projects.remove_member(project_id, user.id, user_id)
    await db.commit()
    return Response(status_code=204)
