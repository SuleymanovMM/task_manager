from dataclasses import dataclass


@dataclass(frozen=True)
class RefreshTokenCommand:
    refresh_token: str


async def handle(command: RefreshTokenCommand, auth_service):
    return await auth_service.refresh(command.refresh_token)
