from fastapi import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from fastapi.responses import Response
from sqlalchemy import text
from app.infrastructure.database.session import get_session_factory

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(): return {"status": "ok"}


@router.get("/ready")
async def ready():
    try:
        async with get_session_factory()() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return Response(content='{"status":"not_ready"}', media_type="application/json", status_code=503)


@router.get("/metrics")
async def metrics(): return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
