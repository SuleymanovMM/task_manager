from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, model_validator
from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.visibility import Visibility
from app.domain.enums.project_role import ProjectRole


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    visibility: Visibility = Visibility.PRIVATE
    start_date: datetime | None = None
    deadline: datetime | None = None

    @model_validator(mode="after")
    def dates(self):
        if self.start_date and self.deadline and self.deadline < self.start_date: raise ValueError(
            "deadline cannot be before start_date")
        return self


class ProjectPatchRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: ProjectStatus | None = None
    visibility: Visibility | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None


class TeamCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class TeamPatchRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class AddMemberRequest(BaseModel):
    user_id: UUID
    role: ProjectRole = ProjectRole.MEMBER


class InvitationCreateRequest(BaseModel):
    invited_user_id: UUID
    expires_in_days: int = Field(default=7, ge=1, le=30)
