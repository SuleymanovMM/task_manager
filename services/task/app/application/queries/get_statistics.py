from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetStatisticsQuery:
    project_id: UUID
    user_id: UUID
    access_token: str
