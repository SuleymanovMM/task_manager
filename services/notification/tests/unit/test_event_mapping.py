from uuid import uuid4

from app.application.services.event_mapper import notification_from_event
from app.domain.enums.notification_type import NotificationType


def test_task_assigned_mapping():
    task_id, user_id = uuid4(), uuid4()
    notification = notification_from_event({
        "event_id": str(uuid4()),
        "event_type": "TaskAssigned",
        "occurred_at": "2026-09-10T10:00:00Z",
        "producer": "task-service",
        "version": 1,
        "payload": {"task_id": str(task_id), "assignee_id": str(user_id), "task_title": "API"},
    })
    assert notification.user_id == user_id
    assert notification.type == NotificationType.TASK_ASSIGNED
    assert notification.related_entity_id == task_id
    assert "API" in notification.message


def test_project_invitation_mapping():
    project_id, user_id = uuid4(), uuid4()
    notification = notification_from_event({
        "event_id": str(uuid4()),
        "event_type": "ProjectInvitationCreated",
        "occurred_at": "2026-09-10T10:00:00Z",
        "producer": "project-service",
        "version": 1,
        "payload": {"project_id": str(project_id), "invited_user_id": str(user_id)},
    })
    assert notification.type == NotificationType.PROJECT_INVITATION
    assert notification.user_id == user_id
