from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class Team:
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, owner_id: UUID, name: str, description: str | None):
        now = datetime.now(timezone.utc)
        return cls(uuid4(), owner_id, name, description, now, now)

    def touch(self): self.updated_at = datetime.now(timezone.utc)
