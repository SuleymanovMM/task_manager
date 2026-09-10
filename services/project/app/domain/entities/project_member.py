from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from app.domain.enums.project_role import ProjectRole


@dataclass
class ProjectMember:
    id: UUID
    project_id: UUID
    user_id: UUID
    role: ProjectRole
    joined_at: datetime

    @classmethod
    def create(cls, project_id, user_id, role):
        return cls(uuid4(), project_id, user_id, role, datetime.now(timezone.utc))
