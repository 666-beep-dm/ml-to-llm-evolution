"""
Cache abstraction with Redis backend and in-memory fallback.
Dependency Inversion: services depend on CachePort, not Redis directly.
"""
from __future__ import annotations
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any

import redis.asyncio as aioredis
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("cache")


# ── Port (interface) ──────────────────────────────────────────────────────────

class CachePort(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any | None: ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def ping(self) -> bool: ...

    @staticmethod
    def make_key(prefix: str, *parts: str) -> str:
        raw = ":".join(parts)
        digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return f"{prefix}:{digest}"


# ── Redis adapter ─────────────────────────────────────────────────────────────

class RedisCache(CachePort):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        self._default_ttl = settings.cache_ttl_seconds

    async def get(self, key: str) -> Any | None:
        try:
            raw = await self._client.get(key)
            return json.loads(raw) if raw else None
        except Exception as exc:
            logger.warning("cache.get_failed", key=key, error=str(exc))
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        try:
            await self._client.setex(
                key, ttl or self._default_ttl, json.dumps(value)
            )
        except Exception as exc:
            logger.warning("cache.set_failed", key=key, error=str(exc))

    async def delete(self, key: str) -> None:
        try:
            await self._client.delete(key)
        except Exception as exc:
            logger.warning("cache.delete_failed", key=key, error=str(exc))

    async def ping(self) -> bool:
        try:
            return await self._client.ping()
        except Exception:
            return False


# ── In-memory fallback ────────────────────────────────────────────────────────

class InMemoryCache(CachePort):
    """Thread-safe in-memory cache. Used if Redis is unavailable."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def get(self, key: str) -> Any | None:
        return self._store.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._store[key] = value  # TTL not enforced in-memory for simplicity

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def ping(self) -> bool:
        return True


# ── Factory ───────────────────────────────────────────────────────────────────

async def create_cache() -> CachePort:
    cache = RedisCache()
    if await cache.ping():
        logger.info("cache.backend", backend="redis")
        return cache
    logger.warning("cache.backend", backend="in-memory", reason="Redis unreachable")
    return InMemoryCache()
