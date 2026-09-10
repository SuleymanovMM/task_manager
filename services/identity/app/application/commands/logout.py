from dataclasses import dataclass


@dataclass(frozen=True)
class LogoutCommand:
    refresh_token: str


async def handle(command: LogoutCommand, auth_service):
    await auth_service.logout(command.refresh_token)
