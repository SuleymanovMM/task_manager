from dataclasses import asdict
from datetime import UTC, datetime
from uuid import UUID

from app.domain.entities.comment import Comment
from app.domain.entities.task import Task
from app.domain.entities.task_history import TaskHistory
from app.domain.enums.priority import Priority
from app.domain.enums.task_status import TaskStatus
from app.domain.exceptions.task_exceptions import (
    CommentNotFoundError,
    ParentTaskNotFoundError,
    TaskAccessDeniedError,
    TaskNotFoundError,
)
from app.domain.events.task_events import TaskCompletedEvent
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.database.repositories.sqlalchemy_comment_repository import SQLAlchemyCommentRepository
from app.infrastructure.database.repositories.sqlalchemy_history_repository import SQLAlchemyHistoryRepository
from app.infrastructure.database.repositories.sqlalchemy_outbox_repository import SQLAlchemyOutboxRepository
from app.infrastructure.database.repositories.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from app.infrastructure.external.project_client import ProjectClient
from app.core.config import settings


class TaskService:
    def __init__(self, db, cache: RedisCache, project_client: ProjectClient):
        self.db = db
        self.tasks = SQLAlchemyTaskRepository(db)
        self.comments = SQLAlchemyCommentRepository(db)
        self.history = SQLAlchemyHistoryRepository(db)
        self.outbox = SQLAlchemyOutboxRepository(db)
        self.cache = cache
        self.project_client = project_client

    @staticmethod
    def _cache_key(task_id: UUID) -> str:
        return f"task:{task_id}"

    async def _membership(self, project_id: UUID, user_id: UUID, access_token: str,
                          required_roles: set[str] | None = None):
        key = f"project_member:{project_id}:{user_id}"
        cached = await self.cache.get_json(key)
        if cached is not None:
            if not cached:
                raise TaskAccessDeniedError("User is not a project member")
            role = cached["role"] if isinstance(cached, dict) else None
            if required_roles and role not in required_roles:
                raise TaskAccessDeniedError("Insufficient project role")
            return role

        membership = await self.project_client.membership(project_id, user_id, access_token)
        ttl = settings.project_member_cache_ttl_seconds
        if membership is None:
            await self.cache.set_json(key, False, ttl)
            raise TaskAccessDeniedError("User is not a project member")
        value = {"role": membership.role}
        await self.cache.set_json(key, value, ttl)
        if required_roles and membership.role not in required_roles:
            raise TaskAccessDeniedError("Insufficient project role")
        return membership.role

    async def create_task(self, req, user_id: UUID, access_token: str) -> Task:
        await self._membership(req.project_id, user_id, access_token, {"OWNER", "MANAGER"})
        if req.parent_task_id:
            parent = await self.tasks.get(req.parent_task_id)
            if parent is None or parent.project_id != req.project_id:
                raise ParentTaskNotFoundError()
        task, event = Task.create(
            req.project_id, user_id, req.title, req.description, req.priority,
            req.deadline, req.estimated_minutes, req.parent_task_id
        )
        await self.tasks.add(task)
        await self.history.add(TaskHistory.create(task.id, user_id, "created", None, "created"))
        await self.outbox.add(event.event_id, event.event_type, event.envelope())
        return task

    @staticmethod
    def _dt(value):
        return datetime.fromisoformat(value) if value else None

    @staticmethod
    def _serialize(task: Task) -> dict:
        return {
            k: (
                v.value if isinstance(v, (TaskStatus, Priority))
                else v.isoformat() if hasattr(v, "isoformat")
                else str(v) if isinstance(v, UUID)
                else v
            )
            for k, v in asdict(task).items()
        }

    @staticmethod
    def _deserialize(cached: dict) -> Task:
        return Task(
            id=UUID(cached["id"]), project_id=UUID(cached["project_id"]), creator_id=UUID(cached["creator_id"]),
            assignee_id=UUID(cached["assignee_id"]) if cached["assignee_id"] else None,
            title=cached["title"], description=cached["description"], status=TaskStatus(cached["status"]),
            priority=Priority(cached["priority"]), deadline=TaskService._dt(cached["deadline"]),
            estimated_minutes=cached["estimated_minutes"], actual_minutes=cached["actual_minutes"],
            progress=cached["progress"],
            parent_task_id=UUID(cached["parent_task_id"]) if cached["parent_task_id"] else None,
            created_at=TaskService._dt(cached["created_at"]), updated_at=TaskService._dt(cached["updated_at"]),
            completed_at=TaskService._dt(cached["completed_at"]),
        )

    async def get_task(self, task_id: UUID, user_id: UUID, access_token: str) -> Task:
        cached = await self.cache.get_json(self._cache_key(task_id))
        if cached:
            task = self._deserialize(cached)
        else:
            task = await self.tasks.get(task_id)
            if task is None:
                raise TaskNotFoundError()
            await self.cache.set_json(self._cache_key(task_id), self._serialize(task), settings.redis_ttl_seconds)
        await self._membership(task.project_id, user_id, access_token)
        return task

    async def list_tasks(self, filters, user_id: UUID, access_token: str, my_tasks=False):
        if filters.project_id:
            await self._membership(filters.project_id, user_id, access_token)
        elif not my_tasks:
            raise TaskAccessDeniedError("project_id is required when listing tasks")
        if my_tasks:
            filters.assignee_id = user_id
        items, total = await self.tasks.list(**filters.model_dump())
        if not filters.project_id and my_tasks:
            visible = []
            # /tasks/me затрагивает разные проекты — проверяем членство перед выдачей.
            for task in items:
                try:
                    await self._membership(task.project_id, user_id, access_token)
                    visible.append(task)
                except TaskAccessDeniedError:
                    continue
            return visible, len(visible)
        return items, total

    async def overdue(self, filters, user_id: UUID, access_token: str):
        items, _ = await self.tasks.get_overdue(page=filters.page, page_size=filters.page_size)
        visible = []
        for task in items:
            try:
                await self._membership(task.project_id, user_id, access_token)
                visible.append(task)
            except TaskAccessDeniedError:
                continue
        return visible, len(visible)

    async def update_task(self, task_id, req, user_id, access_token):
        task = await self.get_task(task_id, user_id, access_token)
        await self._membership(task.project_id, user_id, access_token, {"OWNER", "MANAGER"})
        changes = []
        for field in ("title", "description", "priority", "deadline", "estimated_minutes", "actual_minutes",
                      "progress"):
            if field not in req.model_fields_set:
                continue
            value = getattr(req, field)
            if value == getattr(task, field):
                continue
            old = getattr(task, field)
            if field == "deadline":
                event = task.change_deadline(value, user_id)
                changes.append(
                    (field, str(old) if old is not None else None, str(value) if value is not None else None))
                await self.outbox.add(event.event_id, event.event_type, event.envelope())
            elif field == "progress":
                task.update_progress(value)
                changes.append((field, str(old), str(value)))
            else:
                setattr(task, field, value)
                task.updated_at = datetime.now(UTC)
                changes.append(
                    (field, str(old) if old is not None else None, str(value) if value is not None else None))
        for field, old, new in changes:
            await self.history.add(TaskHistory.create(task.id, user_id, field, old, new))
        await self.tasks.update(task)
        await self.cache.delete(self._cache_key(task_id))
        return task

    async def delete(self, task_id, user_id, access_token):
        task = await self.get_task(task_id, user_id, access_token)
        await self._membership(task.project_id, user_id, access_token, {"OWNER", "MANAGER"})
        await self.tasks.delete(task_id)
        await self.cache.delete(self._cache_key(task_id))

    async def assign(self, task_id, assignee_id, user_id, access_token):
        task = await self.get_task(task_id, user_id, access_token)
        await self._membership(task.project_id, user_id, access_token, {"OWNER", "MANAGER"})
        if assignee_id:
            await self._membership(task.project_id, assignee_id, access_token)
        event = task.assign(assignee_id, user_id)
        await self.history.add(TaskHistory.create(
            task.id, user_id, "assignee_id",
            str(event.previous_assignee_id) if event.previous_assignee_id else None,
            str(assignee_id) if assignee_id else None,
        ))
        await self.tasks.update(task)
        await self.outbox.add(event.event_id, event.event_type, event.envelope())
        await self.cache.delete(self._cache_key(task_id))
        return task

    async def change_status(self, task_id, status, user_id, access_token):
        task = await self.get_task(task_id, user_id, access_token)
        role = await self._membership(task.project_id, user_id, access_token)
        if role not in {"OWNER", "MANAGER"} and task.assignee_id != user_id:
            raise TaskAccessDeniedError("Only assignee, MANAGER or OWNER can change status")
        old = task.status
        event = task.change_status(status, user_id)
        if old == status:
            return task
        await self.history.add(TaskHistory.create(task.id, user_id, "status", old.value, status.value))
        await self.outbox.add(event.event_id, event.event_type, event.envelope())
        if status == TaskStatus.DONE:
            await self.history.add(TaskHistory.create(
                task.id, user_id, "completed_at", None, task.completed_at.isoformat()
            ))
            completed = TaskCompletedEvent(task.id, task.project_id, user_id)
            await self.outbox.add(completed.event_id, completed.event_type, completed.envelope())
        await self.tasks.update(task)
        await self.cache.delete(self._cache_key(task_id))
        return task

    async def add_comment(self, task_id, content, user_id, access_token):
        task = await self.get_task(task_id, user_id, access_token)
        comment = Comment.create(task.id, user_id, content)
        await self.comments.add(comment)
        return comment

    async def list_comments(self, task_id, user_id, access_token, offset, limit):
        await self.get_task(task_id, user_id, access_token)
        return await self.comments.list_for_task(task_id, offset, limit)

    async def update_comment(self, comment_id, content, user_id):
        comment = await self.comments.get(comment_id)
        if comment is None:
            raise CommentNotFoundError()
        if comment.author_id != user_id:
            raise TaskAccessDeniedError("Only comment author can edit it")
        comment.update(content)
        await self.comments.update(comment)
        return comment

    async def delete_comment(self, comment_id, user_id):
        comment = await self.comments.get(comment_id)
        if comment is None:
            raise CommentNotFoundError()
        if comment.author_id != user_id:
            raise TaskAccessDeniedError("Only comment author can delete it")
        await self.comments.delete(comment_id)

    async def history_list(self, task_id, user_id, access_token):
        await self.get_task(task_id, user_id, access_token)
        return await self.history.list_for_task(task_id)

    async def statistics(self, project_id, user_id, access_token):
        await self._membership(project_id, user_id, access_token)
        return await self.tasks.count_project_statistics(project_id)
