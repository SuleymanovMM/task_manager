from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.visibility import Visibility
from app.domain.enums.project_role import ProjectRole
from app.domain.enums.invitation_status import InvitationStatus
from app.domain.enums.team_role import TeamRole


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
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


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class MemberResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    role: ProjectRole
    joined_at: datetime


class TeamMemberResponse(BaseModel):
    id: UUID
    team_id: UUID
    user_id: UUID
    role: TeamRole
    joined_at: datetime


class InvitationResponse(BaseModel):
    id: UUID
    project_id: UUID
    invited_user_id: UUID
    invited_by: UUID
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime


class PaginatedProjects(BaseModel):
    items: list[ProjectResponse]
    total: int
    offset: int
    limit: int


class PaginatedTeams(BaseModel):
    items: list[TeamResponse]
    total: int
    offset: int
    limit: int


class MembershipCheckResponse(BaseModel):
    project_id: UUID
    user_id: UUID
    role: ProjectRole
