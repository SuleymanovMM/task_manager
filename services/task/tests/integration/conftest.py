from uuid import uuid4
import pytest
from app.core.security import CurrentUser
from app.api.dependencies import get_auth, get_task_service

@pytest.fixture
def user_id():
    return uuid4()

@pytest.fixture
def fake_auth(user_id):
    return (CurrentUser(id=user_id, role="USER"), "test-access-token")
