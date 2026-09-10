from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.comment import Comment


class CommentRepository(ABC):
    @abstractmethod
    async def add(self, comment: Comment) -> None: ...

    @abstractmethod
    async def get(self, comment_id: UUID) -> Comment | None: ...

    @abstractmethod
    async def update(self, comment: Comment) -> None: ...

    @abstractmethod
    async def delete(self, comment_id: UUID) -> None: ...

    @abstractmethod
    async def list_for_task(self, task_id: UUID, offset: int, limit: int): ...
