from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AddCommentCommand:
    task_id: UUID
    content: str
    user_id: UUID
    access_token: str
