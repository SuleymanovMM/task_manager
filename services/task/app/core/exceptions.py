from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.domain.exceptions.task_exceptions import (
    TaskNotFoundError,
    InvalidTaskStatusTransitionError,
    TaskAccessDeniedError,
    InvalidProgressError,
    DeadlineValidationError,
    CommentNotFoundError,
    ParentTaskNotFoundError,
    ProjectServiceUnavailableError,
)


def register_exception_handlers(app: FastAPI) -> None:
    mapping = {
        TaskNotFoundError: (404, "Task not found"),
        CommentNotFoundError: (404, "Comment not found"),
        ParentTaskNotFoundError: (400, "Parent task not found"),
        InvalidTaskStatusTransitionError: (409, "Invalid task status transition"),
        TaskAccessDeniedError: (403, "Task access denied"),
        InvalidProgressError: (400, "Invalid progress"),
        DeadlineValidationError: (422, "Invalid deadline"),
        ProjectServiceUnavailableError: (503, "Project Service unavailable"),
    }

    for exception_type, (status_code, detail) in mapping.items():
        async def handler(request: Request, exc: Exception, status_code=status_code, detail=detail):
            return JSONResponse(status_code=status_code, content={"detail": str(exc) or detail})

        app.add_exception_handler(exception_type, handler)
