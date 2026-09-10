from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class LogoutAllCommand:
    user_id: UUID


async def handle(command: LogoutAllCommand, auth_service):
    await auth_service.logout_all(command.user_id)
