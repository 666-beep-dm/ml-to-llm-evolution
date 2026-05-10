"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.services.llm_service import LLMService

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialise shared resources at startup; clean up on shutdown."""
    logger.info("Starting up — model=%s timeout=%ss", settings.model_name, settings.timeout)
    app.state.llm_service = LLMService()
    yield
    logger.info("Shutting down.")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="Middle LLM API",
        version="2.0.0",
        description=(
            "A modular FastAPI service with conversation history, "
            "robust error handling, and pydantic-settings configuration."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1", tags=["Chat"])

    @app.get("/health", tags=["Ops"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "model": settings.model_name}

    return app


app = create_app()
