from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

project_status = postgresql.ENUM(
    "PLANNED", "ACTIVE", "ON_HOLD", "COMPLETED", "ARCHIVED", name="project_status", create_type=False
)
project_visibility = postgresql.ENUM("PRIVATE", "TEAM", name="project_visibility", create_type=False)
team_role = postgresql.ENUM("OWNER", "ADMIN", "MEMBER", name="team_role", create_type=False)
project_role = postgresql.ENUM("OWNER", "MANAGER", "MEMBER", "VIEWER", name="project_role", create_type=False)
invitation_status = postgresql.ENUM(
    "PENDING", "ACCEPTED", "DECLINED", "EXPIRED", name="invitation_status", create_type=False
)


def upgrade():
    bind = op.get_bind()
    # create_type=False выше не даёт create_table повторно выполнить CREATE TYPE.
    for enum in (project_status, project_visibility, team_role, project_role, invitation_status):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", project_status, nullable=False),
        sa.Column("visibility", project_visibility, nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True)),
        sa.Column("deadline", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "team_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", team_role, nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("team_id", "user_id", name="uq_team_member"),
    )
    op.create_table(
        "project_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", project_role, nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_member"),
    )
    op.create_table(
        "project_invitations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("invited_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invited_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", invitation_status, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("project_id", "invited_user_id", "status", name="uq_project_invitation_status"),
    )


def downgrade():
    for table in ("project_invitations", "project_members", "team_members", "teams", "projects"):
        op.drop_table(table)
    for enum in (invitation_status, project_role, team_role, project_visibility, project_status):
        enum.drop(op.get_bind(), checkfirst=True)
