from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user, get_project_service
from app.core.security import CurrentUser


class FakeProjectService:
    async def create_project(self, uid, req):
        from app.domain.entities.project import Project
        return Project.create(uid, req.name, req.description, req.visibility, req.start_date, req.deadline)

    async def list_projects(self, uid, offset, limit):
        return [], 0


async def fake_current_user():
    return CurrentUser(id=uuid4(), role="USER")


def fake_project_service():
    return FakeProjectService()


def test_health():
    with TestClient(app) as c:
        assert c.get('/health').status_code == 200


def test_projects_require_bearer():
    with TestClient(app) as c:
        assert c.get('/api/v1/projects').status_code == 401


def test_jwt_dependency_is_replaceable():
    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[get_project_service] = fake_project_service
    try:
        with TestClient(app) as c:
            assert c.get('/api/v1/projects').status_code == 200
    finally:
        app.dependency_overrides.clear()
