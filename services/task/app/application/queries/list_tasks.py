from dataclasses import dataclass


@dataclass(frozen=True)
class ListTasksQuery:
    filters: object
    user_id: object
    access_token: str
