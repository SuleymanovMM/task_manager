from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.processed_event import ProcessedEvent
from app.infrastructure.database.models.notification_model import ProcessedEventModel


class SqlAlchemyProcessedEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, event_id: UUID) -> ProcessedEvent | None:
        model = await self.session.get(ProcessedEventModel, event_id)
        if not model:
            return None
        return ProcessedEvent(model.event_id, model.event_type, model.processed_at, model.consumer)

    async def add(self, event: ProcessedEvent) -> None:
        self.session.add(ProcessedEventModel(
            event_id=event.event_id,
            event_type=event.event_type,
            processed_at=event.processed_at,
            consumer=event.consumer,
        ))
