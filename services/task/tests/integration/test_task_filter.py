import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes.tasks import router
from app.api.dependencies import get_auth, get_task_service
from app.core.security import CurrentUser
from uuid import uuid4

class FakeService:
    def __init__(self): self.db = type("DB", (), {})()
    async def list_tasks(self, filters, user_id, token, my_tasks=False):
        return [], 0

@pytest.mark.integration
def test_task_filter_contract():
    uid = uuid4()
    app = FastAPI(); app.include_router(router)
    async def auth_override(): return (CurrentUser(id=uid, role="USER"), "token")
    def service_override(): return FakeService()
    app.dependency_overrides[get_auth] = auth_override
    app.dependency_overrides[get_task_service] = service_override
    client = TestClient(app)
    response = client.get("/api/v1/tasks", params={"project_id": str(uuid4()), "status": "TODO", "sort_by": "deadline", "order": "asc"})
    assert response.status_code == 200
    assert response.json()["total"] == 0
