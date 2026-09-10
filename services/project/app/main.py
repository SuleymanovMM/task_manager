import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import configure_logging, request_id_ctx, new_request_id
from app.core.exceptions import register_exception_handlers
from app.api.routes import auth, projects, teams, members, invitations, internal, health
from app.infrastructure.database.session import dispose_engine
from app.infrastructure.messaging.publisher import publisher

configure_logging(settings.log_level)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await publisher.connect()
    except Exception:
        # RabbitMQ может подняться позже приложения — публикация повторится при первой попытке.
        log.warning("RabbitMQ unavailable during startup; publishing will retry")
    try:
        yield
    finally:
        await publisher.close()
        await dispose_engine()


app = FastAPI(
    title="TaskFlow Project Service", version="0.1.0", lifespan=lifespan,
    docs_url="/project/docs", openapi_url="/project/openapi.json", redoc_url="/project/redoc",
    swagger_ui_oauth2_redirect_url="/project/docs/oauth2-redirect",
    swagger_ui_parameters={"persistAuthorization": True},
)
if settings.cors_origin_list:
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True,
                       allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def request_context(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or new_request_id()
    token = request_id_ctx.set(rid)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response
    finally:
        request_id_ctx.reset(token)


app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(teams.router)
app.include_router(members.router)
app.include_router(invitations.router)
app.include_router(internal.router)
app.include_router(health.router)
register_exception_handlers(app)
