from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.api.dependencies import get_current_user_id
from app.infrastructure.cache.redis_client import get_redis


class RateLimiter:
    """Ограничитель запросов на Redis — лимиты общие для всех реплик."""

    def __init__(self, scope: str, limit: int, window_seconds: int) -> None:
        self.scope = scope
        self.limit = limit
        self.window_seconds = window_seconds

    async def _hit(self, redis: Redis, identifier: str) -> None:
        key = f"ratelimit:{self.scope}:{identifier}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, self.window_seconds)
        if count > self.limit:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests, try again later")

    async def by_ip(self, request: Request, redis: Annotated[Redis, Depends(get_redis)]) -> None:
        identifier = request.client.host if request.client else "unknown"
        await self._hit(redis, identifier)

    async def by_user(
            self, user_id: Annotated[UUID, Depends(get_current_user_id)],
            redis: Annotated[Redis, Depends(get_redis)]
    ) -> None:
        await self._hit(redis, str(user_id))
