from datetime import datetime
from uuid import UUID
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.models.base import Base
from app.domain.enums.team_role import TeamRole
from app.domain.enums.project_role import ProjectRole


class TeamMemberModel(Base):
    __tablename__ = "team_members"
    __table_args__ = (UniqueConstraint("team_id", "user_id", name="uq_team_member"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    role: Mapped[TeamRole] = mapped_column(SAEnum(TeamRole, name="team_role", native_enum=True), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ProjectMemberModel(Base):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_member"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    role: Mapped[ProjectRole] = mapped_column(SAEnum(ProjectRole, name="project_role", native_enum=True),
                                              nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
