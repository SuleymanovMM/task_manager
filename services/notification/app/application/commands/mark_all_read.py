from uuid import UUID

from app.domain.repositories.notification_repository import NotificationRepository


class MarkAllNotificationsReadCommand:
    def __init__(self, repo: NotificationRepository) -> None:
        self.repo = repo

    async def execute(self, user_id: UUID) -> None:
        await self.repo.mark_all_read(user_id)
