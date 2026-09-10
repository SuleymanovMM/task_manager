from uuid import UUID
from fastapi import APIRouter, Query, Response, status
from app.api.dependencies import AuthDep, TaskServiceDep
from app.schemas.requests import CommentCreateRequest, CommentPatchRequest
from app.schemas.responses import CommentResponse, PaginatedComments

router = APIRouter(tags=["comments"])


@router.post("/api/v1/tasks/{task_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(task_id: UUID, req: CommentCreateRequest, auth: AuthDep, service: TaskServiceDep):
    user, token = auth
    result = await service.add_comment(task_id, req.content, user.id, token)
    await service.db.commit()
    return result


@router.get("/api/v1/tasks/{task_id}/comments", response_model=PaginatedComments)
async def list_comments(task_id: UUID, auth: AuthDep, service: TaskServiceDep,
                        offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    user, token = auth
    items, total = await service.list_comments(task_id, user.id, token, offset, limit)
    return {"items": items, "offset": offset, "limit": limit, "total": total}


@router.patch("/api/v1/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: UUID, req: CommentPatchRequest, auth: AuthDep, service: TaskServiceDep):
    user, _ = auth
    result = await service.update_comment(comment_id, req.content, user.id)
    await service.db.commit()
    return result


@router.delete("/api/v1/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: UUID, auth: AuthDep, service: TaskServiceDep):
    user, _ = auth
    await service.delete_comment(comment_id, user.id)
    await service.db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
