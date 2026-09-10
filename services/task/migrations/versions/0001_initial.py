"""create task service tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

task_status = postgresql.ENUM(
    "BACKLOG", "TODO", "IN_PROGRESS", "IN_REVIEW", "BLOCKED", "DONE", "CANCELLED",
    name="task_status", create_type=False,
)
task_priority = postgresql.ENUM("LOW", "MEDIUM", "HIGH", "URGENT", name="task_priority", create_type=False)


def upgrade() -> None:
    # create_type=False выше не даёт create_table повторно выполнить CREATE TYPE.
    task_status.create(op.get_bind(), checkfirst=True)
    task_priority.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", task_status, nullable=False, server_default="BACKLOG"),
        sa.Column("priority", task_priority, nullable=False, server_default="MEDIUM"),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("actual_minutes", sa.Integer(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("parent_task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["parent_task_id"], ["tasks.id"], ondelete="SET NULL"),
        sa.CheckConstraint("progress >= 0 AND progress <= 100", name="ck_tasks_progress"),
        sa.CheckConstraint("estimated_minutes IS NULL OR estimated_minutes >= 0", name="ck_tasks_estimated_minutes"),
        sa.CheckConstraint("actual_minutes IS NULL OR actual_minutes >= 0", name="ck_tasks_actual_minutes"),
    )
    op.create_index("idx_tasks_project_id", "tasks", ["project_id"])
    op.create_index("idx_tasks_assignee_id", "tasks", ["assignee_id"])
    op.create_index("idx_tasks_deadline", "tasks", ["deadline"])
    op.create_index("idx_tasks_status", "tasks", ["status"])
    op.create_index("idx_tasks_project_status", "tasks", ["project_id", "status"])

    op.create_table(
        "comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.String(length=5000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_comments_task_id", "comments", ["task_id"])

    op.create_table(
        "task_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_task_history_task_id", "task_history", ["task_id"])

    op.create_table(
        "outbox_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_outbox_unpublished", "outbox_events", ["published_at", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_outbox_unpublished", table_name="outbox_events")
    op.drop_table("outbox_events")
    op.drop_index("idx_task_history_task_id", table_name="task_history")
    op.drop_table("task_history")
    op.drop_index("idx_comments_task_id", table_name="comments")
    op.drop_table("comments")
    op.drop_index("idx_tasks_project_status", table_name="tasks")
    op.drop_index("idx_tasks_status", table_name="tasks")
    op.drop_index("idx_tasks_deadline", table_name="tasks")
    op.drop_index("idx_tasks_assignee_id", table_name="tasks")
    op.drop_index("idx_tasks_project_id", table_name="tasks")
    op.drop_table("tasks")
    task_priority.drop(op.get_bind(), checkfirst=True)
    task_status.drop(op.get_bind(), checkfirst=True)
