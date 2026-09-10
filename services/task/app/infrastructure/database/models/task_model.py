from datetime import datetime
from uuid import UUID as PyUUID
from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.enums.priority import Priority
from app.domain.enums.task_status import TaskStatus
from .base import Base

class TaskModel(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("progress >= 0 AND progress <= 100", name="ck_tasks_progress"),
        CheckConstraint("estimated_minutes IS NULL OR estimated_minutes >= 0", name="ck_tasks_estimated_minutes"),
        CheckConstraint("actual_minutes IS NULL OR actual_minutes >= 0", name="ck_tasks_actual_minutes"),
        Index("idx_tasks_project_id", "project_id"),
        Index("idx_tasks_assignee_id", "assignee_id"),
        Index("idx_tasks_deadline", "deadline"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_project_status", "project_id", "status"),
    )
    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    creator_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    assignee_id: Mapped[PyUUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, name="task_status"), nullable=False, default=TaskStatus.BACKLOG)
    priority: Mapped[Priority] = mapped_column(Enum(Priority, name="task_priority"), nullable=False, default=Priority.MEDIUM)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parent_task_id: Mapped[PyUUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    parent: Mapped["TaskModel | None"] = relationship(remote_side=[id], lazy="selectin")
