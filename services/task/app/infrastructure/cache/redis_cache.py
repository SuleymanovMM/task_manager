import json
import logging
try:
    import redis.asyncio as redis
except ModuleNotFoundError:
    redis = None

from app.core.config import settings

log = logging.getLogger(__name__)


class RedisCache:
    def __init__(self):
        self.client = redis.from_url(settings.redis_url, decode_responses=True) if redis else None

    async def get_json(self, key: str):
        if self.client is None:
            return None
        try:
            value = await self.client.get(key)
            return json.loads(value) if value else None
        except Exception:
            log.warning("Redis GET failed; continuing without cache", extra={"key": key}, exc_info=True)
            return None

    async def set_json(self, key: str, value, ttl: int):
        if self.client is None:
            return
        try:
            await self.client.set(key, json.dumps(value), ex=ttl)
        except Exception:
            log.warning("Redis SET failed; continuing without cache", extra={"key": key}, exc_info=True)

    async def delete(self, key: str):
        if self.client is None:
            return
        try:
            await self.client.delete(key)
        except Exception:
            log.warning("Redis DEL failed; continuing without cache", extra={"key": key}, exc_info=True)

    async def close(self):
        if self.client is not None:
            try:
                await self.client.aclose()
            except Exception:
                log.warning("Redis close failed", exc_info=True)
