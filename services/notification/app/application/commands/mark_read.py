from uuid import UUID

from app.domain.exceptions.notification_exceptions import NotificationNotFoundError
from app.domain.repositories.notification_repository import NotificationRepository


class MarkNotificationReadCommand:
    def __init__(self, repo: NotificationRepository) -> None:
        self.repo = repo

    async def execute(self, notification_id: UUID, user_id: UUID) -> None:
        if not await self.repo.mark_read(notification_id, user_id):
            raise NotificationNotFoundError()
