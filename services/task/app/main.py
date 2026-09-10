import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.dependencies import get_cache
from app.api.routes import auth, comments, health, history, statistics, tasks
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, new_request_id, request_id_ctx
from app.infrastructure.database.session import dispose_engine
from app.infrastructure.messaging.outbox_worker import run_outbox_worker
from app.infrastructure.messaging.publisher import RabbitPublisher

configure_logging(settings.log_level)
log = logging.getLogger(__name__)

rabbit_publisher = RabbitPublisher()
stop_event = asyncio.Event()
worker_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_task
    try:
        try:
            await rabbit_publisher.connect()
        except Exception:
            log.warning("RabbitMQ unavailable during startup; outbox worker will retry", exc_info=True)
        stop_event.clear()
        worker_task = asyncio.create_task(run_outbox_worker(rabbit_publisher, stop_event))
        yield
    finally:
        stop_event.set()
        if worker_task:
            await worker_task
        await rabbit_publisher.close()
        await get_cache().close()
        await dispose_engine()


app = FastAPI(
    title="TaskFlow Task Service", version="0.1.0", lifespan=lifespan,
    docs_url="/task/docs", openapi_url="/task/openapi.json", redoc_url="/task/redoc",
    swagger_ui_oauth2_redirect_url="/task/docs/oauth2-redirect",
    swagger_ui_parameters={"persistAuthorization": True},
)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or new_request_id()
    token = request_id_ctx.set(request_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_ctx.reset(token)


@app.get("/metrics", include_in_schema=False)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    log.exception("unhandled_exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(history.router)
app.include_router(statistics.router)
app.include_router(health.router)
register_exception_handlers(app)
app.add_exception_handler(Exception, unhandled_exception_handler)
