"""
Semantic cache backed by Redis.

Strategy:
  - Store (embedding_vector, answer, chunks) keyed by a UUID.
  - On each query, compare the query embedding against all cached embeddings
    using cosine distance. If distance < threshold → cache hit.

This is a lightweight implementation without a dedicated vector index for the
cache itself (suitable for up to ~10 k cached entries). For larger volumes,
replace with Redis Stack + VSS.
"""

import json
import pickle
from typing import Any

import numpy as np
import redis

from app.core.config import settings
from app.core.logging import logger


def _get_redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=False)


_CACHE_INDEX_KEY = "rag:cache:index"   # hash: uuid → pickled (embedding, payload)


def _cosine_distance(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    return float(1.0 - np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-10))


def get_cached(query_embedding: list[float]) -> dict[str, Any] | None:
    """
    Look for a semantically similar cached answer.

    Returns the cached payload dict or None on cache miss.
    """
    try:
        r = _get_redis()
        all_entries: dict[bytes, bytes] = r.hgetall(_CACHE_INDEX_KEY)

        best_dist = float("inf")
        best_payload: dict | None = None

        for _, raw in all_entries.items():
            cached_embedding, payload = pickle.loads(raw)
            dist = _cosine_distance(query_embedding, cached_embedding)
            if dist < best_dist:
                best_dist = dist
                best_payload = payload

        if best_payload and best_dist < settings.cache_similarity_threshold:
            logger.info("Semantic cache HIT (distance={:.4f})", best_dist)
            return best_payload

        logger.debug("Semantic cache MISS (best_distance={:.4f})", best_dist)
        return None

    except Exception as exc:
        logger.warning("Cache lookup failed: {}", exc)
        return None


def set_cached(query_embedding: list[float], payload: dict[str, Any]) -> None:
    """Store a query result in the semantic cache."""
    try:
        import uuid
        r = _get_redis()
        key = str(uuid.uuid4())
        r.hset(_CACHE_INDEX_KEY, key, pickle.dumps((query_embedding, payload)))
        # TTL is applied to the whole hash key — refresh on every write
        r.expire(_CACHE_INDEX_KEY, settings.cache_ttl_seconds)
        logger.debug("Cached answer under key={}", key)
    except Exception as exc:
        logger.warning("Cache write failed: {}", exc)


def health_check() -> bool:
    """Return True if Redis is reachable."""
    try:
        return _get_redis().ping()
    except Exception:
        return False
