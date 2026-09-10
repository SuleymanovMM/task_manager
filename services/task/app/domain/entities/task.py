from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.enums.priority import Priority
from app.domain.enums.task_status import STATUS_TRANSITIONS, TaskStatus
from app.domain.exceptions.task_exceptions import (
    DeadlineValidationError,
    InvalidProgressError,
    InvalidTaskStatusTransitionError,
)
from app.domain.events.task_events import (
    TaskAssignedEvent,
    TaskCreatedEvent,
    TaskDeadlineChangedEvent,
    TaskStatusChangedEvent,
)


@dataclass
class Task:
    id: UUID
    project_id: UUID
    creator_id: UUID
    assignee_id: UUID | None
    title: str
    description: str | None
    status: TaskStatus
    priority: Priority
    deadline: datetime | None
    estimated_minutes: int | None
    actual_minutes: int | None
    progress: int
    parent_task_id: UUID | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    @classmethod
    def create(
            cls,
            project_id: UUID,
            creator_id: UUID,
            title: str,
            description: str | None,
            priority: Priority,
            deadline: datetime | None,
            estimated_minutes: int | None,
            parent_task_id: UUID | None,
    ) -> tuple["Task", TaskCreatedEvent]:
        now = datetime.now(UTC)
        cls.validate_deadline(deadline, now)
        task = cls(
            id=uuid4(),
            project_id=project_id,
            creator_id=creator_id,
            assignee_id=None,
            title=title,
            description=description,
            status=TaskStatus.BACKLOG,
            priority=priority,
            deadline=deadline,
            estimated_minutes=estimated_minutes,
            actual_minutes=None,
            progress=0,
            parent_task_id=parent_task_id,
            created_at=now,
            updated_at=now,
            completed_at=None,
        )
        event = TaskCreatedEvent(task.id, project_id, creator_id, task.title)
        return task, event

    @staticmethod
    def validate_deadline(deadline: datetime | None, now: datetime | None = None) -> None:
        if deadline is None:
            return
        current = now or datetime.now(UTC)
        if deadline.tzinfo is None:
            raise DeadlineValidationError("deadline must contain timezone information")
        if deadline < current:
            raise DeadlineValidationError("deadline must be greater than or equal to now")

    def change_status(self, new_status: TaskStatus, changed_by: UUID) -> TaskStatusChangedEvent:
        if new_status == self.status:
            return TaskStatusChangedEvent(self.id, self.project_id, self.status, self.status, changed_by)
        if new_status not in STATUS_TRANSITIONS[self.status]:
            raise InvalidTaskStatusTransitionError(
                f"{self.status.value} -> {new_status.value} is not allowed"
            )

        old_status = self.status
        now = datetime.now(UTC)
        self.status = new_status
        self.updated_at = now

        if new_status == TaskStatus.TODO:
            self.progress = 0
        elif new_status == TaskStatus.IN_PROGRESS:
            if self.progress == 0:
                self.progress = 1
        elif new_status == TaskStatus.DONE:
            self.progress = 100
            self.completed_at = now
        elif new_status == TaskStatus.CANCELLED:
            # Отмена не сбрасывает прогресс.
            pass

        return TaskStatusChangedEvent(
            self.id, self.project_id, old_status, new_status, changed_by
        )

    def assign(self, assignee_id: UUID | None, assigned_by: UUID) -> TaskAssignedEvent:
        previous = self.assignee_id
        self.assignee_id = assignee_id
        self.updated_at = datetime.now(UTC)
        return TaskAssignedEvent(
            self.id, self.project_id, assignee_id, assigned_by, previous
        )

    def update_progress(self, value: int) -> None:
        if not 0 <= value <= 100:
            raise InvalidProgressError("progress must be between 0 and 100")
        if self.status == TaskStatus.TODO and value != 0:
            raise InvalidProgressError("TODO task must have 0% progress")
        if self.status == TaskStatus.IN_PROGRESS and not 1 <= value <= 99:
            raise InvalidProgressError("IN_PROGRESS task must have progress from 1 to 99")
        if self.status == TaskStatus.DONE and value != 100:
            raise InvalidProgressError("DONE task must have 100% progress")
        self.progress = value
        self.updated_at = datetime.now(UTC)

    def change_deadline(self, deadline: datetime | None, changed_by: UUID) -> TaskDeadlineChangedEvent:
        self.validate_deadline(deadline)
        old = self.deadline
        self.deadline = deadline
        self.updated_at = datetime.now(UTC)
        return TaskDeadlineChangedEvent(self.id, self.project_id, old, deadline, changed_by)
