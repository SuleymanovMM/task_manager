from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.project import Project
from app.domain.enums.project_status import ProjectStatus
from app.domain.entities.project_member import ProjectMember
from app.infrastructure.database.models import ProjectModel, ProjectMemberModel


class SQLAlchemyProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity):
        self.session.add(ProjectModel(**entity.__dict__))
        await self.session.flush()
        return entity

    async def get(self, project_id):
        m = await self.session.get(ProjectModel, project_id)
        return None if not m else Project(**{c: getattr(m, c) for c in Project.__dataclass_fields__})

    async def update(self, entity):
        m = await self.session.get(ProjectModel, entity.id)
        if not m:
            return entity
        for c in entity.__dataclass_fields__:
            setattr(m, c, getattr(entity, c))
        await self.session.flush()
        return entity

    async def list_for_user(self, user_id, offset, limit):
        base = select(ProjectModel).join(ProjectMemberModel, ProjectMemberModel.project_id == ProjectModel.id).where(
            ProjectMemberModel.user_id == user_id, ProjectModel.status != ProjectStatus.ARCHIVED)
        total = (await self.session.scalar(select(func.count()).select_from(base.subquery()))) or 0
        rows = (
            await self.session.scalars(base.order_by(ProjectModel.created_at.desc()).offset(offset).limit(limit))).all()
        return [Project(**{c: getattr(m, c) for c in Project.__dataclass_fields__}) for m in rows], total

    async def get_member(self, project_id, user_id):
        m = await self.session.scalar(select(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id,
                                                                       ProjectMemberModel.user_id == user_id))
        return None if not m else ProjectMember(m.id, m.project_id, m.user_id, m.role, m.joined_at)

    async def list_members(self, project_id):
        rows = (await self.session.scalars(
            select(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id).order_by(
                ProjectMemberModel.joined_at))).all()
        return [ProjectMember(m.id, m.project_id, m.user_id, m.role, m.joined_at) for m in rows]

    async def add_member(self, entity):
        self.session.add(ProjectMemberModel(**entity.__dict__))
        await self.session.flush()
        return entity

    async def remove_member(self, project_id, user_id):
        m = await self.session.scalar(select(ProjectMemberModel).where(ProjectMemberModel.project_id == project_id,
                                                                       ProjectMemberModel.user_id == user_id))
        if m:
            await self.session.delete(m)
            await self.session.flush()
