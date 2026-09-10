from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

engine = None
SessionLocal = None


def get_engine():
    global engine
    if engine is None:
        engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    return engine


def get_session_factory():
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return SessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def dispose_engine() -> None:
    global engine, SessionLocal
    if engine is not None:
        await engine.dispose()
    engine = None
    SessionLocal = None
