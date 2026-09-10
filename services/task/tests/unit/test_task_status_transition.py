from datetime import UTC, datetime
from uuid import uuid4
import pytest
from app.domain.entities.task import Task
from app.domain.enums.priority import Priority
from app.domain.enums.task_status import TaskStatus
from app.domain.exceptions.task_exceptions import InvalidTaskStatusTransitionError

def make_task(status=TaskStatus.BACKLOG):
    task, _ = Task.create(uuid4(), uuid4(), "Test", None, Priority.MEDIUM, None, None, None)
    task.status = status
    return task

def test_valid_status_transition():
    task = make_task(TaskStatus.IN_PROGRESS)
    event = task.change_status(TaskStatus.IN_REVIEW, uuid4())
    assert event.new_status == TaskStatus.IN_REVIEW

def test_invalid_status_transition():
    task = make_task(TaskStatus.TODO)
    with pytest.raises(InvalidTaskStatusTransitionError):
        task.change_status(TaskStatus.DONE, uuid4())

def test_done_sets_progress_and_completed_at():
    task = make_task(TaskStatus.IN_REVIEW)
    task.change_status(TaskStatus.DONE, uuid4())
    assert task.progress == 100
    assert task.completed_at is not None
