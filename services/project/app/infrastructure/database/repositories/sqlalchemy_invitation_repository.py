from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.project_invitation import ProjectInvitation
from app.infrastructure.database.models import ProjectInvitationModel


class SQLAlchemyInvitationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, e):
        self.session.add(ProjectInvitationModel(**e.__dict__))
        await self.session.flush()
        return e

    async def get(self, invitation_id):
        m = await self.session.get(ProjectInvitationModel, invitation_id)
        return None if not m else ProjectInvitation(
            **{c: getattr(m, c) for c in ProjectInvitation.__dataclass_fields__})

    async def update(self, e):
        m = await self.session.get(ProjectInvitationModel, e.id)
        if m:
            for c in e.__dataclass_fields__:
                setattr(m, c, getattr(e, c))
            await self.session.flush()
        return e

    async def list_for_user(self, user_id):
        rows = (await self.session.scalars(
            select(ProjectInvitationModel).where(ProjectInvitationModel.invited_user_id == user_id).order_by(
                ProjectInvitationModel.created_at.desc()))).all()
        return [ProjectInvitation(**{c: getattr(m, c) for c in ProjectInvitation.__dataclass_fields__}) for m in rows]
