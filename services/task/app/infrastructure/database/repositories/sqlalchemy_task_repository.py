from datetime import UTC, datetime
from uuid import UUID
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.task import Task
from app.domain.enums.task_status import TaskStatus
from app.infrastructure.database.models.task_model import TaskModel


class SQLAlchemyTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def to_entity(row: TaskModel) -> Task:
        return Task(
            id=row.id, project_id=row.project_id, creator_id=row.creator_id,
            assignee_id=row.assignee_id, title=row.title, description=row.description,
            status=row.status, priority=row.priority, deadline=row.deadline,
            estimated_minutes=row.estimated_minutes, actual_minutes=row.actual_minutes,
            progress=row.progress, parent_task_id=row.parent_task_id,
            created_at=row.created_at, updated_at=row.updated_at, completed_at=row.completed_at,
        )

    @staticmethod
    def apply_entity(row: TaskModel, task: Task) -> None:
        row.assignee_id = task.assignee_id
        row.title = task.title
        row.description = task.description
        row.status = task.status
        row.priority = task.priority
        row.deadline = task.deadline
        row.estimated_minutes = task.estimated_minutes
        row.actual_minutes = task.actual_minutes
        row.progress = task.progress
        row.parent_task_id = task.parent_task_id
        row.updated_at = task.updated_at
        row.completed_at = task.completed_at

    async def add(self, task: Task) -> None:
        self.session.add(TaskModel(
            id=task.id, project_id=task.project_id, creator_id=task.creator_id,
            assignee_id=task.assignee_id, title=task.title, description=task.description,
            status=task.status, priority=task.priority, deadline=task.deadline,
            estimated_minutes=task.estimated_minutes, actual_minutes=task.actual_minutes,
            progress=task.progress, parent_task_id=task.parent_task_id,
            created_at=task.created_at, updated_at=task.updated_at, completed_at=task.completed_at,
        ))
        # parent_task_id —self-referential FK, автопорядок вставки при flush не спасает;
        # если в той же транзакции добавляются зависимые строки (история), нужен явный flush.
        await self.session.flush()

    async def get(self, task_id: UUID) -> Task | None:
        row = await self.session.get(TaskModel, task_id)
        return self.to_entity(row) if row else None

    async def update(self, task: Task) -> None:
        row = await self.session.get(TaskModel, task.id)
        if row is None:
            return
        self.apply_entity(row, task)

    async def delete(self, task_id: UUID) -> None:
        await self.session.execute(delete(TaskModel).where(TaskModel.id == task_id))

    async def list(self, *, project_id=None, assignee_id=None, status=None, priority=None,
                   deadline_from=None, deadline_to=None, created_from=None, created_to=None,
                   search=None, sort_by="created_at", order="desc", page=1, page_size=20,
                   creator_id=None):
        conditions = []
        for column, value in ((TaskModel.project_id, project_id), (TaskModel.assignee_id, assignee_id),
                             (TaskModel.status, status), (TaskModel.priority, priority),
                             (TaskModel.creator_id, creator_id)):
            if value is not None:
                conditions.append(column == value)
        if deadline_from: conditions.append(TaskModel.deadline >= deadline_from)
        if deadline_to: conditions.append(TaskModel.deadline <= deadline_to)
        if created_from: conditions.append(TaskModel.created_at >= created_from)
        if created_to: conditions.append(TaskModel.created_at <= created_to)
        if search:
            pattern = f"%{search}%"
            conditions.append(or_(TaskModel.title.ilike(pattern), TaskModel.description.ilike(pattern)))
        query = select(TaskModel).where(*conditions)
        sort_column = {
            "created_at": TaskModel.created_at,
            "updated_at": TaskModel.updated_at,
            "deadline": TaskModel.deadline,
            "priority": TaskModel.priority,
            "status": TaskModel.status,
        }[sort_by]
        query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())
        count_query = select(func.count()).select_from(TaskModel).where(*conditions)
        total = int((await self.session.execute(count_query)).scalar_one())
        query = query.offset((page - 1) * page_size).limit(page_size)
        rows = (await self.session.execute(query)).scalars().all()
        return [self.to_entity(row) for row in rows], total

    async def get_overdue(self, *, page=1, page_size=20):
        now = datetime.now(UTC)
        excluded = (TaskModel.status != TaskStatus.DONE, TaskModel.status != TaskStatus.CANCELLED)
        conditions = (TaskModel.deadline.is_not(None), TaskModel.deadline < now, *excluded)
        count = int((await self.session.execute(select(func.count()).select_from(TaskModel).where(*conditions))).scalar_one())
        rows = (await self.session.execute(
            select(TaskModel).where(*conditions).order_by(TaskModel.deadline.asc()).offset((page-1)*page_size).limit(page_size)
        )).scalars().all()
        return [self.to_entity(row) for row in rows], count

    async def count_project_statistics(self, project_id: UUID) -> dict:
        rows = await self.session.execute(
            select(TaskModel.status, func.count(TaskModel.id))
            .where(TaskModel.project_id == project_id)
            .group_by(TaskModel.status)
        )
        by_status = {status.value: count for status, count in rows.all()}
        total = sum(by_status.values())
        return {"total": total, "by_status": by_status}
