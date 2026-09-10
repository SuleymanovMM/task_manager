from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from app.domain.enums.project_role import ProjectRole
from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.visibility import Visibility
from app.domain.exceptions.project_exceptions import ProjectAlreadyArchivedError


@dataclass
class Project:
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    status: ProjectStatus
    visibility: Visibility
    start_date: datetime | None
    deadline: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, owner_id: UUID, name: str, description: str | None, visibility: Visibility,
               start_date: datetime | None, deadline: datetime | None):
        now = datetime.now(timezone.utc)
        return cls(uuid4(), owner_id, name, description, ProjectStatus.PLANNED, visibility, start_date, deadline, now,
                   now)

    def archive(self):
        if self.status == ProjectStatus.ARCHIVED:
            raise ProjectAlreadyArchivedError()
        self.status = ProjectStatus.ARCHIVED
        self.updated_at = datetime.now(timezone.utc)

    def can_view(self, role: ProjectRole | None) -> bool:
        return role is not None

    def can_modify(self, user_id: UUID, role: ProjectRole) -> bool:
        return role == ProjectRole.OWNER and self.owner_id == user_id

    def can_manage_members(self, role: ProjectRole) -> bool:
        return role in {ProjectRole.OWNER, ProjectRole.MANAGER}

    def can_assign_role(self, actor_role: ProjectRole, target_role: ProjectRole) -> bool:
        if actor_role == ProjectRole.OWNER:
            return target_role in {ProjectRole.MANAGER, ProjectRole.MEMBER, ProjectRole.VIEWER}
        return actor_role == ProjectRole.MANAGER and target_role in {ProjectRole.MEMBER, ProjectRole.VIEWER}
