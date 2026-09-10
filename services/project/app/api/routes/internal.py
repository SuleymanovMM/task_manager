from uuid import UUID
from fastapi import APIRouter, HTTPException
from app.api.dependencies import CurrentUserDep, ProjectServiceDep
from app.schemas.responses import MembershipCheckResponse

router = APIRouter(prefix="/api/v1/internal", tags=["internal"])


@router.get("/projects/{project_id}/members/{user_id}", response_model=MembershipCheckResponse)
async def membership(project_id: UUID, user_id: UUID, _user: CurrentUserDep, projects: ProjectServiceDep):
    member = await projects.check_membership(project_id, user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    return {"project_id": project_id, "user_id": user_id, "role": member.role}
