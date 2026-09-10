from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class TaskHistory:
    id: UUID
    task_id: UUID
    changed_by: UUID
    field_name: str
    old_value: str | None
    new_value: str | None
    created_at: datetime

    @classmethod
    def create(
            cls,
            task_id: UUID,
            changed_by: UUID,
            field_name: str,
            old_value: str | None,
            new_value: str | None,
    ) -> "TaskHistory":
        return cls(
            uuid4(),
            task_id,
            changed_by,
            field_name,
            old_value,
            new_value,
            datetime.now(UTC),
        )
