from abc import ABC, abstractmethod
from uuid import UUID


class OutboxRepository(ABC):
    @abstractmethod
    async def add(self, event_id: UUID, event_type: str, payload: dict) -> None: ...

    @abstractmethod
    async def get_unpublished(self, limit: int = 100): ...

    @abstractmethod
    async def mark_published(self, event_id: UUID) -> None: ...
