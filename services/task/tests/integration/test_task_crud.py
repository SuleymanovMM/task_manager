import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes import tasks
from app.api.dependencies import get_auth, get_task_service
from app.api.routes.tasks import router
from app.domain.entities.task import Task
from app.domain.enums.priority import Priority

class FakeService:
    def __init__(self, task):
        self.task = task
        self.deleted_task_id = None
        self.db = type("DB", (), {"commit": self.commit})()
    async def commit(self): pass
    async def create_task(self, req, user_id, token): return self.task
    async def delete(self, task_id, user_id, token): self.deleted_task_id = task_id

@pytest.mark.integration
def test_create_task_endpoint(user_id, fake_auth):
    from uuid import uuid4
    from datetime import UTC, datetime
    task, _ = Task.create(uuid4(), user_id, "Build API", None, Priority.MEDIUM, None, None, None)
    service = FakeService(task)
    app = FastAPI()
    app.include_router(router)
    async def auth_override(): return fake_auth
    def service_override(): return service
    app.dependency_overrides[get_auth] = auth_override
    app.dependency_overrides[get_task_service] = service_override
    client = TestClient(app)
    response = client.post("/api/v1/tasks", json={
        "project_id": str(task.project_id),
        "title": "Build API",
        "priority": "MEDIUM"
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Build API"


@pytest.mark.integration
def test_delete_task_endpoint(user_id, fake_auth):
    from uuid import uuid4
    task, _ = Task.create(uuid4(), user_id, "Build API", None, Priority.MEDIUM, None, None, None)
    service = FakeService(task)
    app = FastAPI()
    app.include_router(router)
    async def auth_override(): return fake_auth
    def service_override(): return service
    app.dependency_overrides[get_auth] = auth_override
    app.dependency_overrides[get_task_service] = service_override
    client = TestClient(app)
    response = client.delete(f"/api/v1/tasks/{task.id}")
    assert response.status_code == 204
    assert service.deleted_task_id == task.id
