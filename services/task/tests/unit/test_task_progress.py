from datetime import UTC, datetime
from uuid import uuid4
import pytest
from app.domain.entities.task import Task
from app.domain.enums.priority import Priority
from app.domain.enums.task_status import TaskStatus
from app.domain.exceptions.task_exceptions import InvalidProgressError

def make_task(status=TaskStatus.IN_PROGRESS):
    task, _ = Task.create(uuid4(), uuid4(), "Test", None, Priority.MEDIUM, None, None, None)
    task.status = status
    return task

def test_progress_must_be_1_to_99_in_progress():
    task = make_task()
    with pytest.raises(InvalidProgressError):
        task.update_progress(0)

def test_progress_100_is_allowed_for_done():
    task = make_task(TaskStatus.DONE)
    task.update_progress(100)
    assert task.progress == 100
