from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class ProcessedEvent:
    event_id: UUID
    event_type: str
    processed_at: datetime
    consumer: str
