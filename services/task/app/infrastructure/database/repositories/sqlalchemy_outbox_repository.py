from datetime import UTC, datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.models.outbox_model import OutboxEventModel

class SQLAlchemyOutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, event_id: UUID, event_type: str, payload: dict):
        self.session.add(OutboxEventModel(id=event_id, event_type=event_type, payload=payload))

    async def get_unpublished(self, limit: int = 100):
        return (await self.session.execute(
            select(OutboxEventModel).where(OutboxEventModel.published_at.is_(None))
            .order_by(OutboxEventModel.created_at.asc()).limit(limit)
        )).scalars().all()

    async def mark_published(self, event_id: UUID):
        row = await self.session.get(OutboxEventModel, event_id)
        if row:
            row.published_at = datetime.now(UTC)
