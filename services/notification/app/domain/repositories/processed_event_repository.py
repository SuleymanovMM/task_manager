from typing import Protocol
from uuid import UUID

from app.domain.entities.processed_event import ProcessedEvent


class ProcessedEventRepository(Protocol):
    async def get(self, event_id: UUID) -> ProcessedEvent | None: ...
    async def add(self, event: ProcessedEvent) -> None: ...
