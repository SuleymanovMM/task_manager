from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AssignTaskCommand:
    task_id: UUID
    assignee_id: UUID | None
    user_id: UUID
    access_token: str
