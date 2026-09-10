from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions.identity_exceptions import (
    InvalidCredentialsError,
    RefreshTokenExpiredError,
    RefreshTokenRevokedError,
    TokenExpiredError,
    TokenRevokedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


async def user_already_exists_handler(_: Request, exc: UserAlreadyExistsError):
    return _error(409, "USER_ALREADY_EXISTS", str(exc))


async def invalid_credentials_handler(_: Request, exc: InvalidCredentialsError):
    return _error(401, "INVALID_CREDENTIALS", str(exc))


async def user_not_found_handler(_: Request, exc: UserNotFoundError):
    return _error(404, "USER_NOT_FOUND", str(exc))


async def token_expired_handler(_: Request, exc: (TokenExpiredError | RefreshTokenExpiredError)):
    return _error(401, "TOKEN_EXPIRED", str(exc))


async def token_revoked_handler(_: Request, exc: (TokenRevokedError | RefreshTokenRevokedError)):
    return _error(401, "TOKEN_REVOKED", str(exc))
