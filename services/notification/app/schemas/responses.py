from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.enums.notification_type import NotificationType


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    related_entity_id: UUID | None
    is_read: bool
    created_at: datetime


class PaginatedNotifications(BaseModel):
    items: list[NotificationResponse]
    page: int
    page_size: int
    total: int
    pages: int
