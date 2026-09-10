import math
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import AuthDep, TaskServiceDep
from app.domain.enums.priority import Priority
from app.domain.enums.task_status import TaskStatus
from app.schemas.requests import (
    AssignTaskRequest,
    ChangeStatusRequest,
    TaskCreateRequest,
    TaskFilters,
    TaskPatchRequest,
)
from app.schemas.responses import PaginatedTasks, TaskResponse

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def page_response(items, page: int, page_size: int, total: int) -> dict:
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": math.ceil(total / page_size) if total else 0,
    }


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(req: TaskCreateRequest, auth: AuthDep, service: TaskServiceDep):
    user, token = auth
    task = await service.create_task(req, user.id, token)
    await service.db.commit()
    return task


@router.get("/me", response_model=PaginatedTasks)
async def my_tasks(
    auth: AuthDep,
    service: TaskServiceDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    user, token = auth
    filters = TaskFilters(page=page, page_size=page_size)
    items, total = await service.list_tasks(filters, user.id, token, my_tasks=True)
    return page_response(items, page, page_size, total)


@router.get("/overdue", response_model=PaginatedTasks)
async def overdue(
    auth: AuthDep,
    service: TaskServiceDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    user, token = auth
    filters = TaskFilters(page=page, page_size=page_size)
    items, total = await service.overdue(filters, user.id, token)
    return page_response(items, page, page_size, total)


@router.get("", response_model=PaginatedTasks)
async def list_tasks(
    auth: AuthDep,
    service: TaskServiceDep,
    project_id: UUID | None = None,
    assignee_id: UUID | None = None,
    status_: TaskStatus | None = Query(None, alias="status"),
    priority: Priority | None = None,
    deadline_from: datetime | None = None,
    deadline_to: datetime | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    search: str | None = None,
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    user, token = auth
    filters = TaskFilters(
        project_id=project_id,
        assignee_id=assignee_id,
        status=status_,
        priority=priority,
        deadline_from=deadline_from,
        deadline_to=deadline_to,
        created_from=created_from,
        created_to=created_to,
        search=search,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )
    items, total = await service.list_tasks(filters, user.id, token)
    return page_response(items, page, page_size, total)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, auth: AuthDep, service: TaskServiceDep):
    user, token = auth
    return await service.get_task(task_id, user.id, token)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    req: TaskPatchRequest,
    auth: AuthDep,
    service: TaskServiceDep,
):
    user, token = auth
    task = await service.update_task(task_id, req, user.id, token)
    await service.db.commit()
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    auth: AuthDep,
    service: TaskServiceDep,
):
    user, token = auth
    await service.delete(task_id, user.id, token)
    await service.db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: UUID,
    req: AssignTaskRequest,
    auth: AuthDep,
    service: TaskServiceDep,
):
    user, token = auth
    task = await service.assign(task_id, req.assignee_id, user.id, token)
    await service.db.commit()
    return task


@router.post("/{task_id}/status", response_model=TaskResponse)
async def change_status(
    task_id: UUID,
    req: ChangeStatusRequest,
    auth: AuthDep,
    service: TaskServiceDep,
):
    user, token = auth
    task = await service.change_status(task_id, req.status, user.id, token)
    await service.db.commit()
    return task
