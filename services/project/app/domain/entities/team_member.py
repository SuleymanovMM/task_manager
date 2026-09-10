from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from app.domain.enums.team_role import TeamRole


@dataclass
class TeamMember:
    id: UUID
    team_id: UUID
    user_id: UUID
    role: TeamRole
    joined_at: datetime

    @classmethod
    def create(cls, team_id, user_id, role):
        return cls(uuid4(), team_id, user_id, role, datetime.now(timezone.utc))
