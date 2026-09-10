import uuid
from contextlib import asynccontextmanager

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import (
    invalid_credentials_handler,
    token_expired_handler,
    token_revoked_handler,
    user_already_exists_handler,
    user_not_found_handler,
)
from app.core.logs import configure_logging, request_id_var
from app.domain.exceptions.identity_exceptions import (
    InvalidCredentialsError,
    RefreshTokenExpiredError,
    RefreshTokenRevokedError,
    TokenExpiredError,
    TokenRevokedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.infrastructure.cache.redis_client import dispose_redis
from app.infrastructure.database.session import dispose_engine

configure_logging(settings.log_level)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    log.info("application_start environment=%s", settings.environment)
    yield
    await dispose_engine()
    await dispose_redis()
    log.info("application_shutdown")


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    log.exception("unhandled_exception: %s", exc)
    return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}})


app = FastAPI(
    title=settings.app_name, debug=settings.debug, lifespan=lifespan,
    docs_url="/identity/docs", openapi_url="/identity/openapi.json", redoc_url="/identity/redoc",
    swagger_ui_oauth2_redirect_url="/identity/docs/oauth2-redirect",
    swagger_ui_parameters={"persistAuthorization": True},
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"],
        allow_headers=["*"]
    )


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get(settings.request_id_header) or str(uuid.uuid4())
    token = request_id_var.set(request_id)
    try:
        response = await call_next(request)
    finally:
        request_id_var.reset(token)
    response.headers[settings.request_id_header] = request_id
    return response


app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
app.add_exception_handler(UserNotFoundError, user_not_found_handler)
app.add_exception_handler(TokenExpiredError, token_expired_handler)
app.add_exception_handler(RefreshTokenExpiredError, token_expired_handler)
app.add_exception_handler(TokenRevokedError, token_revoked_handler)
app.add_exception_handler(RefreshTokenRevokedError, token_revoked_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(auth_router)
app.include_router(health_router)
