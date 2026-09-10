from dataclasses import dataclass
from uuid import UUID
from app.domain.enums.priority import Priority
from app.domain.enums.task_status import TaskStatus


@dataclass(frozen=True)
class TaskDTO:
    id: UUID
    project_id: UUID
    creator_id: UUID
    assignee_id: UUID | None
    title: str
    status: TaskStatus
    priority: Priority
    progress: int
