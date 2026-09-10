from datetime import datetime
from uuid import UUID as PyUUID
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class TaskHistoryModel(Base):
    __tablename__ = "task_history"
    __table_args__ = (Index("idx_task_history_task_id", "task_id"),)
    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    task_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    changed_by: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
