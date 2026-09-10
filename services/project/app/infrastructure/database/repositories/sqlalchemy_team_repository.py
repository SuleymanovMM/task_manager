from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.team import Team
from app.domain.entities.team_member import TeamMember
from app.infrastructure.database.models import TeamModel, TeamMemberModel


class SQLAlchemyTeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, e):
        self.session.add(TeamModel(**e.__dict__))
        await self.session.flush()
        return e

    async def get(self, team_id):
        m = await self.session.get(TeamModel, team_id)
        return None if not m else Team(**{c: getattr(m, c) for c in Team.__dataclass_fields__})

    async def update(self, e):
        m = await self.session.get(TeamModel, e.id)
        if m:
            for c in e.__dataclass_fields__:
                setattr(m, c, getattr(e, c))
            await self.session.flush()
        return e

    async def delete(self, team_id):
        m = await self.session.get(TeamModel, team_id)
        if m:
            await self.session.delete(m)
            await self.session.flush()

    async def list_for_user(self, user_id, offset, limit):
        base = select(TeamModel).join(TeamMemberModel, TeamMemberModel.team_id == TeamModel.id).where(
            TeamMemberModel.user_id == user_id)
        total = (await self.session.scalar(select(func.count()).select_from(base.subquery()))) or 0
        rows = (
            await self.session.scalars(base.order_by(TeamModel.created_at.desc()).offset(offset).limit(limit))).all()
        return [Team(**{c: getattr(m, c) for c in Team.__dataclass_fields__}) for m in rows], total

    async def get_member(self, team_id, user_id):
        m = await self.session.scalar(
            select(TeamMemberModel).where(TeamMemberModel.team_id == team_id, TeamMemberModel.user_id == user_id))
        return None if not m else TeamMember(m.id, m.team_id, m.user_id, m.role, m.joined_at)

    async def add_member(self, e):
        self.session.add(TeamMemberModel(**e.__dict__))
        await self.session.flush()
        return e
