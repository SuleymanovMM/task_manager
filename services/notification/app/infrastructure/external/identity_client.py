import httpx

from app.core.config import settings


class InvalidCredentialsError(Exception):
    pass


class IdentityUnavailableError(Exception):
    pass


async def login_via_identity(login: str, password: str) -> dict:
    """Форма Authorize в Swagger шлёт username/password сюда — реальный логин у Identity."""
    url = f"{settings.identity_service_url.rstrip('/')}/api/v1/auth/login"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json={"login": login, "password": password})
    except (httpx.HTTPError, OSError) as exc:
        raise IdentityUnavailableError("Identity Service is unavailable") from exc
    if response.status_code == 401:
        raise InvalidCredentialsError("Incorrect username or password")
    if response.status_code != 200:
        raise IdentityUnavailableError(f"Identity Service returned {response.status_code}")
    return response.json()
