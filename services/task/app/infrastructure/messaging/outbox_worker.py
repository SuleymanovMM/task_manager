import asyncio
import logging

from app.core.config import settings
from app.infrastructure.database.session import get_session_factory
from app.infrastructure.database.repositories.sqlalchemy_outbox_repository import SQLAlchemyOutboxRepository
from app.infrastructure.messaging.publisher import RabbitPublisher

log = logging.getLogger(__name__)


async def run_outbox_worker(publisher: RabbitPublisher, stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            async with get_session_factory()() as session:
                repo = SQLAlchemyOutboxRepository(session)
                events = await repo.get_unpublished()
                for event in events:
                    try:
                        await publisher.publish(event.payload)
                        await repo.mark_published(event.id)
                        await session.commit()
                    except Exception:
                        await session.rollback()
                        log.exception("Failed to publish outbox event", extra={"event_id": str(event.id)})
                        break
        except Exception:
            log.exception("Outbox worker cycle failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=settings.outbox_poll_seconds)
        except asyncio.TimeoutError:
            pass
