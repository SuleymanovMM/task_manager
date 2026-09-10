from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from app.domain.enums.priority import Priority
from app.domain.enums.task_status import TaskStatus

class TaskCreateRequest(BaseModel):
    project_id: UUID
    title: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=10000)
    priority: Priority = Priority.MEDIUM
    deadline: datetime | None = None
    estimated_minutes: int | None = Field(default=None, ge=0)
    parent_task_id: UUID | None = None

class TaskPatchRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=10000)
    priority: Priority | None = None
    deadline: datetime | None = None
    estimated_minutes: int | None = Field(default=None, ge=0)
    actual_minutes: int | None = Field(default=None, ge=0)
    progress: int | None = Field(default=None, ge=0, le=100)

class AssignTaskRequest(BaseModel):
    assignee_id: UUID | None = None

class ChangeStatusRequest(BaseModel):
    status: TaskStatus

class CommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)

class CommentPatchRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)

class TaskFilters(BaseModel):
    project_id: UUID | None = None
    assignee_id: UUID | None = None
    status: TaskStatus | None = None
    priority: Priority | None = None
    deadline_from: datetime | None = None
    deadline_to: datetime | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    search: str | None = None
    sort_by: str = "created_at"
    order: str = "desc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        allowed = {"created_at", "updated_at", "deadline", "priority", "status"}
        if value not in allowed:
            raise ValueError(f"sort_by must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("order")
    @classmethod
    def validate_order(cls, value: str) -> str:
        if value not in {"asc", "desc"}:
            raise ValueError("order must be asc or desc")
        return value
