from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.task_history import TaskHistory
from app.infrastructure.database.models.history_model import TaskHistoryModel

class SQLAlchemyHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, history: TaskHistory):
        self.session.add(TaskHistoryModel(
            id=history.id, task_id=history.task_id, changed_by=history.changed_by,
            field_name=history.field_name, old_value=history.old_value,
            new_value=history.new_value, created_at=history.created_at
        ))

    async def list_for_task(self, task_id: UUID):
        rows = (await self.session.execute(
            select(TaskHistoryModel).where(TaskHistoryModel.task_id == task_id).order_by(TaskHistoryModel.created_at.asc())
        )).scalars().all()
        return [TaskHistory(r.id, r.task_id, r.changed_by, r.field_name, r.old_value, r.new_value, r.created_at) for r in rows]
