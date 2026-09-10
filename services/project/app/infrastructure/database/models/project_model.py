from datetime import datetime
from uuid import UUID
from sqlalchemy import String, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.models.base import Base
from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.visibility import Visibility


class ProjectModel(Base):
    __tablename__ = "projects"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(SAEnum(ProjectStatus, name="project_status", native_enum=True),
                                                  nullable=False, default=ProjectStatus.PLANNED)
    visibility: Mapped[Visibility] = mapped_column(SAEnum(Visibility, name="project_visibility", native_enum=True),
                                                   nullable=False, default=Visibility.PRIVATE)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
