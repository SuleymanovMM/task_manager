from fastapi import APIRouter, Response
from sqlalchemy import text
from app.infrastructure.database.session import get_engine

router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/ready")
async def ready():
    try:
        async with get_engine().connect() as connection:
            await connection.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return Response(content='{"status":"not_ready"}', media_type="application/json", status_code=503)
