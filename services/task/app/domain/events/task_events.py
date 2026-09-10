from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    producer: ClassVar[str] = "task-service"
    version: ClassVar[int] = 1
    event_type: ClassVar[str] = ""

    event_id: UUID = field(default_factory=uuid4, init=False)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC), init=False)

    def payload(self) -> dict:
        raise NotImplementedError

    def envelope(self) -> dict:
        return {
            "event_id": str(self.event_id), "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(), "producer": self.producer,
            "version": self.version, "payload": self.payload(),
        }


@dataclass(frozen=True)
class TaskCreatedEvent(DomainEvent):
    event_type: ClassVar[str] = "TaskCreated"

    task_id: UUID
    project_id: UUID
    creator_id: UUID
    title: str

    def payload(self) -> dict:
        return {"task_id": str(self.task_id), "project_id": str(self.project_id),
                "creator_id": str(self.creator_id), "title": self.title}


@dataclass(frozen=True)
class TaskAssignedEvent(DomainEvent):
    event_type: ClassVar[str] = "TaskAssigned"

    task_id: UUID
    project_id: UUID
    assignee_id: UUID | None
    assigned_by: UUID
    previous_assignee_id: UUID | None

    def payload(self) -> dict:
        return {"task_id": str(self.task_id), "project_id": str(self.project_id),
                "assignee_id": str(self.assignee_id) if self.assignee_id else None,
                "assigned_by": str(self.assigned_by),
                "previous_assignee_id": str(self.previous_assignee_id) if self.previous_assignee_id else None}


@dataclass(frozen=True)
class TaskStatusChangedEvent(DomainEvent):
    event_type: ClassVar[str] = "TaskStatusChanged"

    task_id: UUID
    project_id: UUID
    old_status: object
    new_status: object
    changed_by: UUID

    def payload(self) -> dict:
        return {"task_id": str(self.task_id), "project_id": str(self.project_id),
                "old_status": self.old_status.value, "new_status": self.new_status.value,
                "changed_by": str(self.changed_by)}


@dataclass(frozen=True)
class TaskCompletedEvent(DomainEvent):
    event_type: ClassVar[str] = "TaskCompleted"

    task_id: UUID
    project_id: UUID
    completed_by: UUID

    def payload(self) -> dict:
        return {"task_id": str(self.task_id), "project_id": str(self.project_id),
                "completed_by": str(self.completed_by)}


@dataclass(frozen=True)
class TaskDeadlineChangedEvent(DomainEvent):
    event_type: ClassVar[str] = "TaskDeadlineChanged"

    task_id: UUID
    project_id: UUID
    old_deadline: datetime | None
    new_deadline: datetime | None
    changed_by: UUID

    def payload(self) -> dict:
        return {"task_id": str(self.task_id), "project_id": str(self.project_id),
                "old_deadline": self.old_deadline.isoformat() if self.old_deadline else None,
                "new_deadline": self.new_deadline.isoformat() if self.new_deadline else None,
                "changed_by": str(self.changed_by)}
