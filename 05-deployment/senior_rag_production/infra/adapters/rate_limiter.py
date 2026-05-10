"""SlowAPI + Redis rate limiter adapter."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from infra.config import settings


class RateLimiterAdapter:
    def __init__(self) -> None:
        self.limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[
                f"{settings.rate_limit_requests}"
                f"/{settings.rate_limit_window_seconds}second"
            ],
            storage_uri=settings.redis_url,
        )
