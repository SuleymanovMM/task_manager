from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.task_history import TaskHistory


class HistoryRepository(ABC):
    @abstractmethod
    async def add(self, history: TaskHistory) -> None: ...

    @abstractmethod
    async def list_for_task(self, task_id: UUID) -> list[TaskHistory]: ...
