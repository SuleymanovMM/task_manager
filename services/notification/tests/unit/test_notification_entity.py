from datetime import datetime, timezone
from uuid import uuid4

from app.domain.entities.notification import Notification
from app.domain.enums.notification_type import NotificationType


def test_notification_created_unread():
    notification = Notification.create(
        user_id=uuid4(), type=NotificationType.TASK_ASSIGNED,
        title="Новая задача", message="Вам назначили задачу", related_entity_id=uuid4(),
        created_at=datetime.now(timezone.utc),
    )
    assert notification.is_read is False


def test_mark_as_read():
    notification = Notification.create(
        user_id=uuid4(), type=NotificationType.TASK_COMPLETED,
        title="Готово", message="Задача выполнена", related_entity_id=None,
        created_at=datetime.now(timezone.utc),
    )
    notification.mark_as_read()
    assert notification.is_read is True
