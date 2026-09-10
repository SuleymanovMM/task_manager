from uuid import UUID
from fastapi import APIRouter
from app.api.dependencies import AuthDep, TaskServiceDep
from app.schemas.responses import HistoryResponse

router = APIRouter(prefix="/api/v1", tags=["history"])

@router.get("/tasks/{task_id}/history", response_model=list[HistoryResponse])
async def history(task_id: UUID, auth: AuthDep, service: TaskServiceDep):
    user, token = auth
    return await service.history_list(task_id, user.id, token)
