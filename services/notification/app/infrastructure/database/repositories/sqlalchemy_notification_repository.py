from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.notification import Notification
from app.domain.enums.notification_type import NotificationType
from app.infrastructure.database.models.notification_model import NotificationModel


class SqlAlchemyNotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _to_entity(model: NotificationModel) -> Notification:
        return Notification(model.id, model.user_id, model.type, model.title, model.message, model.related_entity_id, model.is_read, model.created_at)

    async def add(self, notification: Notification) -> None:
        self.session.add(NotificationModel(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            related_entity_id=notification.related_entity_id,
            is_read=notification.is_read,
            created_at=notification.created_at,
        ))

    async def get_for_user(self, user_id: UUID, *, page: int, page_size: int, type: NotificationType | None, is_read: bool | None, from_date: datetime | None, to_date: datetime | None) -> tuple[list[Notification], int]:
        stmt = select(NotificationModel).where(NotificationModel.user_id == user_id)
        count_stmt = select(func.count()).select_from(NotificationModel).where(NotificationModel.user_id == user_id)
        for condition in [
            NotificationModel.type == type if type else None,
            NotificationModel.is_read == is_read if is_read is not None else None,
            NotificationModel.created_at >= from_date if from_date else None,
            NotificationModel.created_at <= to_date if to_date else None,
        ]:
            if condition is not None:
                stmt = stmt.where(condition)
                count_stmt = count_stmt.where(condition)
        stmt = stmt.order_by(NotificationModel.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        models = (await self.session.scalars(stmt)).all()
        total = int((await self.session.scalar(count_stmt)) or 0)
        return [self._to_entity(m) for m in models], total

    async def get(self, notification_id: UUID) -> Notification | None:
        model = await self.session.get(NotificationModel, notification_id)
        return self._to_entity(model) if model else None

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> bool:
        result = await self.session.execute(update(NotificationModel).where(NotificationModel.id == notification_id, NotificationModel.user_id == user_id).values(is_read=True))
        return result.rowcount > 0

    async def mark_all_read(self, user_id: UUID) -> None:
        await self.session.execute(update(NotificationModel).where(NotificationModel.user_id == user_id, NotificationModel.is_read.is_(False)).values(is_read=True))
