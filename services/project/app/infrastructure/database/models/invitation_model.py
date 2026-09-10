from datetime import datetime
from uuid import UUID
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.models.base import Base
from app.domain.enums.invitation_status import InvitationStatus


class ProjectInvitationModel(Base):
    __tablename__ = "project_invitations"
    __table_args__ = (UniqueConstraint("project_id", "invited_user_id", "status", name="uq_project_invitation_status"),)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    invited_user_id: Mapped[UUID] = mapped_column(nullable=False)
    invited_by: Mapped[UUID] = mapped_column(nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(
        SAEnum(InvitationStatus, name="invitation_status", native_enum=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
