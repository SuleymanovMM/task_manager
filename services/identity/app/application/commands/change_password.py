from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ChangePasswordCommand:
    user_id: UUID
    current_password: str
    new_password: str


async def handle(command: ChangePasswordCommand, auth_service):
    await auth_service.change_password(command.user_id, command.current_password, command.new_password)
