"""Application factory and lifespan."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.router import router
from app.api.metrics import metrics_router
from infra.config import settings
from infra.logging_config import configure_logging
from infra.container import Container

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(
        "startup",
        extra={"model": settings.model_name, "env": settings.app_env},
    )
    container = await Container.create()
    app.state.container = container
    app.state.limiter = container.rate_limiter.limiter
    yield
    await container.close()
    logger.info("shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Senior RAG Production API",
        version="3.0.0",
        description=(
            "Streaming RAG API with Redis caching, "
            "rate limiting, and Prometheus metrics."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.include_router(router,        prefix="/api/v1", tags=["RAG Chat"])
    app.include_router(metrics_router,                  tags=["Observability"])

    Instrumentator(
        should_group_status_codes=True,
        excluded_handlers=["/health", "/metrics"],
    ).instrument(app).expose(app)

    return app


app = create_app()
