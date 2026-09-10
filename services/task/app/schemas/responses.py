from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.domain.enums.priority import Priority
from app.domain.enums.task_status import TaskStatus

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    creator_id: UUID
    assignee_id: UUID | None
    title: str
    description: str | None
    status: TaskStatus
    priority: Priority
    deadline: datetime | None
    estimated_minutes: int | None
    actual_minutes: int | None
    progress: int
    parent_task_id: UUID | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    task_id: UUID
    author_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

class HistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    task_id: UUID
    changed_by: UUID
    field_name: str
    old_value: str | None
    new_value: str | None
    created_at: datetime

class PaginatedTasks(BaseModel):
    items: list[TaskResponse]
    page: int
    page_size: int
    total: int
    pages: int

class PaginatedComments(BaseModel):
    items: list[CommentResponse]
    offset: int
    limit: int
    total: int

class StatisticsResponse(BaseModel):
    project_id: UUID
    total: int
    by_status: dict[str, int]
