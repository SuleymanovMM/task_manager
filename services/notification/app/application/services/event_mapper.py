from datetime import datetime, timezone
from uuid import UUID

from app.domain.entities.notification import Notification
from app.domain.enums.notification_type import NotificationType

SUPPORTED_EVENTS = {
    "TaskAssigned",
    "TaskStatusChanged",
    "TaskCompleted",
    "TaskDeadlineChanged",
    "ProjectMemberAdded",
    "ProjectInvitationCreated",
}


def _dt(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def notification_from_event(envelope: dict) -> Notification:
    event_type = envelope["event_type"]
    payload = envelope["payload"]
    occurred_at = _dt(envelope.get("occurred_at"))

    if event_type == "TaskAssigned":
        return Notification.create(
            user_id=UUID(payload["assignee_id"]), type=NotificationType.TASK_ASSIGNED,
            title="Новая задача", message=f"Вам назначена задача «{payload.get('task_title', 'без названия')}»",
            related_entity_id=UUID(payload["task_id"]), created_at=occurred_at,
        )
    if event_type == "TaskStatusChanged":
        user_id = payload.get("assignee_id") or payload.get("changed_by")
        if not user_id:
            raise ValueError("TaskStatusChanged payload has no recipient")
        return Notification.create(
            user_id=UUID(user_id), type=NotificationType.TASK_STATUS_CHANGED,
            title="Статус изменён", message=f"Статус задачи изменён на {payload.get('new_status', 'UNKNOWN')}",
            related_entity_id=UUID(payload["task_id"]), created_at=occurred_at,
        )
    if event_type == "TaskCompleted":
        user_id = payload.get("assignee_id") or payload.get("project_owner_id")
        if not user_id:
            raise ValueError("TaskCompleted payload has no recipient")
        return Notification.create(
            user_id=UUID(user_id), type=NotificationType.TASK_COMPLETED,
            title="Задача завершена", message=f"Задача «{payload.get('task_title', 'без названия')}» выполнена",
            related_entity_id=UUID(payload["task_id"]), created_at=occurred_at,
        )
    if event_type == "TaskDeadlineChanged":
        user_id = payload.get("assignee_id")
        if not user_id:
            raise ValueError("TaskDeadlineChanged payload has no recipient")
        return Notification.create(
            user_id=UUID(user_id), type=NotificationType.TASK_DEADLINE_CHANGED,
            title="Изменён дедлайн", message=f"Дедлайн задачи изменён на {payload.get('new_deadline', 'новое значение')}",
            related_entity_id=UUID(payload["task_id"]), created_at=occurred_at,
        )
    if event_type == "ProjectMemberAdded":
        return Notification.create(
            user_id=UUID(payload["user_id"]), type=NotificationType.PROJECT_MEMBER_ADDED,
            title="Вы добавлены в проект", message="Вас добавили в проект",
            related_entity_id=UUID(payload["project_id"]), created_at=occurred_at,
        )
    if event_type == "ProjectInvitationCreated":
        return Notification.create(
            user_id=UUID(payload["invited_user_id"]), type=NotificationType.PROJECT_INVITATION,
            title="Приглашение в проект", message="Вас пригласили в проект",
            related_entity_id=UUID(payload["project_id"]), created_at=occurred_at,
        )
    raise ValueError(f"Unsupported event type: {event_type}")
