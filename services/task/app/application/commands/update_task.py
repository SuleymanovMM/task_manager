from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateTaskCommand:
    task_id: UUID
    request: object
    user_id: UUID
    access_token: str
