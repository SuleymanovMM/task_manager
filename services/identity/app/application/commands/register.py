from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None


async def handle(command: RegisterUserCommand, auth_service):
    return await auth_service.register(**command.__dict__)
