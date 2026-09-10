from datetime import datetime
from uuid import UUID

from app.domain.enums.notification_type import NotificationType
from app.domain.repositories.notification_repository import NotificationRepository


class ListNotificationsQuery:
    def __init__(self, repo: NotificationRepository) -> None:
        self.repo = repo

    async def execute(self, user_id: UUID, *, page: int, page_size: int, type: NotificationType | None = None, is_read: bool | None = None, from_date: datetime | None = None, to_date: datetime | None = None):
        return await self.repo.get_for_user(user_id, page=page, page_size=page_size, type=type, is_read=is_read, from_date=from_date, to_date=to_date)
