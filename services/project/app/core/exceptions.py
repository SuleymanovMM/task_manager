from fastapi import Request
from fastapi.responses import JSONResponse
from app.domain.exceptions.project_exceptions import (
    CannotInviteSelfError,
    InvalidInvitationStatusError,
    InvitationExpiredError,
    InvitationNotFoundError,
    MemberAlreadyExistsError,
    ProjectAccessDeniedError,
    ProjectAlreadyArchivedError,
    ProjectNotFoundError,
    TeamAccessDeniedError,
    TeamNotFoundError,
)


def register_exception_handlers(app):
    mapping = {
        ProjectNotFoundError: (404, "Project not found"),
        ProjectAccessDeniedError: (403, "Project access denied"),
        TeamNotFoundError: (404, "Team not found"),
        MemberAlreadyExistsError: (409, "Member already exists"),
        InvitationNotFoundError: (404, "Invitation not found"),
        InvitationExpiredError: (409, "Invitation expired"),
        InvalidInvitationStatusError: (409, "Invalid invitation status"),
        CannotInviteSelfError: (400, "Cannot invite yourself"),
        ProjectAlreadyArchivedError: (409, "Project already archived"),
        TeamAccessDeniedError: (403, "Team access denied"),
    }
    for exc_type, (code, detail) in mapping.items():
        async def handler(request: Request, exc: Exception, code=code, detail=detail):
            return JSONResponse(status_code=code, content={"detail": detail})

        app.add_exception_handler(exc_type, handler)
