from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateTaskCommand:
    request: object
    user_id: UUID
    access_token: str
