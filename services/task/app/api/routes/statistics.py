from uuid import UUID
from fastapi import APIRouter
from app.api.dependencies import AuthDep, TaskServiceDep
from app.schemas.responses import StatisticsResponse

router = APIRouter(prefix="/api/v1/projects", tags=["statistics"])

@router.get("/{project_id}/statistics", response_model=StatisticsResponse)
async def statistics(project_id: UUID, auth: AuthDep, service: TaskServiceDep):
    user, token = auth
    result = await service.statistics(project_id, user.id, token)
    return {"project_id": project_id, **result}
