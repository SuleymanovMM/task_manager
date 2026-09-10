from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetUserByIdQuery:
    user_id: UUID


async def handle(query: GetUserByIdQuery, auth_service):
    return await auth_service.get_user(query.user_id)
