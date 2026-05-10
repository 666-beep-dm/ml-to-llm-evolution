"""Redis cache adapter."""

import logging
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)
_PREFIX = "rag:cache:"


class RedisCache:
    def __init__(self, client: aioredis.Redis) -> None:
        self._client = client

    @classmethod
    async def create(cls, url: str) -> "RedisCache":
        client = aioredis.from_url(url, decode_responses=True, socket_timeout=3.0)
        return cls(client)

    async def get(self, key: str) -> str | None:
        try:
            return await self._client.get(f"{_PREFIX}{key}")
        except Exception as exc:
            logger.warning("redis_get_failed", extra={"error": str(exc)})
            return None

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        try:
            await self._client.setex(f"{_PREFIX}{key}", ttl, value)
        except Exception as exc:
            logger.warning("redis_set_failed", extra={"error": str(exc)})

    async def ping(self) -> str:
        try:
            await self._client.ping()
            return "ok"
        except Exception:
            return "unavailable"

    async def close(self) -> None:
        await self._client.aclose()
