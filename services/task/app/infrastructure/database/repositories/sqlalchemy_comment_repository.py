from uuid import UUID
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.comment import Comment
from app.infrastructure.database.models.comment_model import CommentModel


class SQLAlchemyCommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def to_entity(row: CommentModel) -> Comment:
        return Comment(row.id, row.task_id, row.author_id, row.content, row.created_at, row.updated_at)

    async def add(self, comment: Comment):
        self.session.add(CommentModel(
            id=comment.id, task_id=comment.task_id, author_id=comment.author_id,
            content=comment.content, created_at=comment.created_at, updated_at=comment.updated_at
        ))

    async def get(self, comment_id: UUID):
        row = await self.session.get(CommentModel, comment_id)
        return self.to_entity(row) if row else None

    async def update(self, comment: Comment):
        row = await self.session.get(CommentModel, comment.id)
        if row:
            row.content, row.updated_at = comment.content, comment.updated_at

    async def delete(self, comment_id: UUID):
        await self.session.execute(delete(CommentModel).where(CommentModel.id == comment_id))

    async def list_for_task(self, task_id: UUID, offset: int, limit: int):
        q = select(CommentModel).where(CommentModel.task_id == task_id).order_by(CommentModel.created_at.asc())
        count = int((await self.session.execute(
            select(func.count()).select_from(CommentModel).where(CommentModel.task_id == task_id)
        )).scalar_one())
        rows = (await self.session.execute(q.offset(offset).limit(limit))).scalars().all()
        return [self.to_entity(r) for r in rows], count
