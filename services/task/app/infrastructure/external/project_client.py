import asyncio
import logging
from uuid import UUID
import httpx
from pydantic import BaseModel
from app.core.config import settings
from app.domain.exceptions.task_exceptions import ProjectServiceUnavailableError

log = logging.getLogger(__name__)


class ProjectMembership(BaseModel):
    project_id: UUID
    user_id: UUID
    role: str


class ProjectClient:
    def __init__(self):
        self.base_url = settings.project_service_url.rstrip("/")

    async def membership(self, project_id: UUID, user_id: UUID, access_token: str) -> ProjectMembership | None:
        url = f"{self.base_url}/api/v1/internal/projects/{project_id}/members/{user_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        last_error = None
        for attempt in range(settings.project_service_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=settings.project_service_timeout_seconds,
                    limits=httpx.Limits(max_connections=100),
                ) as client:
                    response = await client.get(url, headers=headers)
                    if response.status_code == 200:
                        return ProjectMembership.model_validate(response.json())
                    if response.status_code == 404:
                        return None
                    response.raise_for_status()
            except (httpx.HTTPError, OSError) as exc:
                last_error = exc
                if attempt < settings.project_service_retries:
                    await asyncio.sleep(0.1)
        log.error("Project Service unavailable", exc_info=last_error)
        raise ProjectServiceUnavailableError("Project Service is unavailable")
