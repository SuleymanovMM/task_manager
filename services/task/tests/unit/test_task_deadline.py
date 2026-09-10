from datetime import UTC, datetime, timedelta
from uuid import uuid4
import pytest
from app.domain.entities.task import Task
from app.domain.enums.priority import Priority
from app.domain.exceptions.task_exceptions import DeadlineValidationError

def test_past_deadline_rejected():
    with pytest.raises(DeadlineValidationError):
        Task.create(uuid4(), uuid4(), "Test", None, Priority.LOW, datetime.now(UTC) - timedelta(minutes=1), None, None)

def test_timezone_aware_deadline_accepted():
    task, _ = Task.create(uuid4(), uuid4(), "Test", None, Priority.LOW, datetime.now(UTC) + timedelta(days=1), None, None)
    assert task.deadline is not None
