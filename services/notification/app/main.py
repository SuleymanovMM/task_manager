import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.notifications import router as notification_router
from app.core.config import settings
from app.core.exceptions import not_found_handler
from app.core.logging import configure_logging, request_id_var
from app.domain.exceptions.notification_exceptions import NotificationNotFoundError
from app.infrastructure.database.session import dispose_engine
from app.infrastructure.messaging.connection import RabbitConnection
from app.infrastructure.messaging.consumer import start_consumer

configure_logging(settings.log_level)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    rabbit = RabbitConnection()
    try:
        await rabbit.connect()
        _, queue, dlx = await rabbit.setup()
        await start_consumer(queue, dlx)
    except Exception:
        # HTTP API не зависит от RabbitMQ — падение брокера не должно валить весь сервис.
        log.warning("RabbitMQ unavailable during startup; events will not be consumed", exc_info=True)
    app.state.rabbit = rabbit
    log.info("notification_service_started")
    try:
        yield
    finally:
        await rabbit.close()
        await dispose_engine()
        log.info("notification_service_stopped")


app = FastAPI(
    title=settings.app_name, debug=settings.debug, lifespan=lifespan,
    docs_url="/notification/docs", openapi_url="/notification/openapi.json", redoc_url="/notification/redoc",
    swagger_ui_oauth2_redirect_url="/notification/docs/oauth2-redirect",
    swagger_ui_parameters={"persistAuthorization": True},
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = request_id_var.set(request_id)
    try:
        response = await call_next(request)
    finally:
        request_id_var.reset(token)
    response.headers["X-Request-ID"] = request_id
    return response


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    log.exception("unhandled_exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.add_exception_handler(NotificationNotFoundError, not_found_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.include_router(auth_router)
app.include_router(notification_router)
app.include_router(health_router)
