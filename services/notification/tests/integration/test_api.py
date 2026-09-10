from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_current_user, get_notification_repo
from app.main import app


class FakeRepo:
    async def get_for_user(self, user_id, *, page, page_size, type, is_read, from_date, to_date):
        return [], 0

    async def mark_read(self, notification_id, user_id):
        return True

    async def mark_all_read(self, user_id):
        return None


@pytest.mark.asyncio
async def test_list_notifications_requires_no_service_call(monkeypatch):
    user_id = uuid4()
    app.dependency_overrides[get_current_user] = lambda: user_id
    app.dependency_overrides[get_notification_repo] = lambda: FakeRepo()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/notifications")
        assert response.status_code == 200
        assert response.json()["total"] == 0
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_unread_notifications_endpoint():
    user_id = uuid4()
    app.dependency_overrides[get_current_user] = lambda: user_id
    app.dependency_overrides[get_notification_repo] = lambda: FakeRepo()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/notifications/unread?page=1&page_size=10")
        assert response.status_code == 200
        assert response.json()["page_size"] == 10
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_mark_read_returns_204():
    user_id = uuid4()
    app.dependency_overrides[get_current_user] = lambda: user_id
    app.dependency_overrides[get_notification_repo] = lambda: FakeRepo()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/api/v1/notifications/{uuid4()}/read")
        assert response.status_code == 204
    finally:
        app.dependency_overrides.clear()
