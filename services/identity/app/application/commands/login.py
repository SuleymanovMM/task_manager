from dataclasses import dataclass


@dataclass(frozen=True)
class LoginCommand:
    login: str
    password: str


async def handle(command: LoginCommand, auth_service):
    return await auth_service.login(login=command.login, password=command.password)
