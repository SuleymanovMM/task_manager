import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_auth, get_task_service
from app.api.routes import tasks
from app.core.security import CurrentUser
from app.domain.entities.task import Task
from app.domain.enums.priority import Priority
from uuid import uuid4
from datetime import UTC, datetime

class FakeService:
    def __init__(self, task):
        self.task = task
        self.db = type("DB", (), {"commit": self.commit})()
    async def commit(self): pass
    async def assign(self, task_id, assignee_id, user_id, token): return self.task

@pytest.mark.integration
def test_assign_endpoint(user_id, fake_auth):
    task, _ = Task.create(uuid4(), user_id, "Task", None, Priority.MEDIUM, None, None, None)
    service = FakeService(task)
    app = FastAPI()
    app.include_router(tasks.router)

    async def auth_override():
        return fake_auth

    def service_override():
        return service

    app.dependency_overrides[get_auth] = auth_override
    app.dependency_overrides[get_task_service] = service_override

    client = TestClient(app)
    response = client.post(
        f"/api/v1/tasks/{task.id}/assign",
        json={"assignee_id": str(uuid4())},
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(task.id)
