from dataclasses import dataclass


@dataclass(frozen=True)
class GetOverdueTasksQuery:
    filters: object
    user_id: object
    access_token: str
