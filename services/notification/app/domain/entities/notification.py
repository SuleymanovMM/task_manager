from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.enums.notification_type import NotificationType


@dataclass(slots=True)
class Notification:
    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    related_entity_id: UUID | None
    is_read: bool
    created_at: datetime

    def mark_as_read(self) -> None:
        self.is_read = True

    @classmethod
    def create(
        cls,
        *,
        user_id: UUID,
        type: NotificationType,
        title: str,
        message: str,
        related_entity_id: UUID | None,
        created_at: datetime,
    ) -> "Notification":
        return cls(uuid4(), user_id, type, title, message, related_entity_id, False, created_at)
