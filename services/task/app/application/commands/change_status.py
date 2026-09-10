from dataclasses import dataclass
from uuid import UUID
from app.domain.enums.task_status import TaskStatus


@dataclass(frozen=True)
class ChangeStatusCommand:
    task_id: UUID
    status: TaskStatus
    user_id: UUID
    access_token: str
