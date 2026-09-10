from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.application.services.notification_consumer import process_event


@pytest.mark.asyncio
async def test_duplicate_event_is_ignored(monkeypatch):
    calls = {"processed": 0, "added": 0}

    class FakeSession:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def commit(self): pass

    class FakeProcessedRepo:
        async def get(self, _):
            calls["processed"] += 1
            return object() if calls["processed"] == 2 else None
        async def add(self, _): pass

    class FakeNotificationRepo:
        async def add(self, _): calls["added"] += 1

    monkeypatch.setattr("app.application.services.notification_consumer.session_factory", lambda: FakeSession())
    monkeypatch.setattr("app.application.services.notification_consumer.SqlAlchemyProcessedEventRepository", lambda _: FakeProcessedRepo())
    monkeypatch.setattr("app.application.services.notification_consumer.SqlAlchemyNotificationRepository", lambda _: FakeNotificationRepo())

    event = {
        "event_id": str(uuid4()), "event_type": "TaskAssigned", "occurred_at": datetime.now(timezone.utc).isoformat(),
        "payload": {"task_id": str(uuid4()), "assignee_id": str(uuid4()), "task_title": "Test"},
    }
    assert await process_event(event, "test") is True
    assert await process_event(event, "test") is False
    assert calls["added"] == 1
