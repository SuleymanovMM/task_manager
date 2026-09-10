import logging
from datetime import datetime, timezone
from uuid import UUID

from app.application.services.event_mapper import notification_from_event
from app.domain.entities.processed_event import ProcessedEvent
from app.infrastructure.database.repositories.sqlalchemy_notification_repository import SqlAlchemyNotificationRepository
from app.infrastructure.database.repositories.sqlalchemy_processed_event_repository import SqlAlchemyProcessedEventRepository
from app.infrastructure.database.session import session_factory

log = logging.getLogger(__name__)


async def process_event(envelope: dict, consumer_name: str) -> bool:
    event_id = UUID(envelope["event_id"])
    async with session_factory() as session:
        processed_repo = SqlAlchemyProcessedEventRepository(session)
        if await processed_repo.get(event_id):
            return False

        notification = notification_from_event(envelope)
        notification_repo = SqlAlchemyNotificationRepository(session)
        await notification_repo.add(notification)
        await processed_repo.add(ProcessedEvent(
            event_id=event_id,
            event_type=envelope["event_type"],
            processed_at=datetime.now(timezone.utc),
            consumer=consumer_name,
        ))
        await session.commit()
        return True
