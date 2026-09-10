from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class Comment:
    id: UUID
    task_id: UUID
    author_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, task_id: UUID, author_id: UUID, content: str) -> "Comment":
        now = datetime.now(UTC)
        return cls(uuid4(), task_id, author_id, content, now, now)

    def update(self, content: str) -> None:
        self.content = content
        self.updated_at = datetime.now(UTC)
