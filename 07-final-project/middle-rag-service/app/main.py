"""
Mini-RAG Service — application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.middleware import (
    RequestLoggingMiddleware,
    value_error_handler,
    runtime_error_handler,
    generic_error_handler,
)
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store
from app.core.config import get_settings
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────────────────────
    settings = get_settings()
    logger.info(f"Starting Mini-RAG Service | model={settings.model_name}")
    embedding_service.load()
    vector_store.init()
    logger.info("Service ready.")
    yield
    # ── Shutdown ───────────────────────────────────────────────────────────────
    logger.info("Shutting down Mini-RAG Service.")


app = FastAPI(
    title="Mini-RAG Service",
    description=(
        "A production-grade Retrieval-Augmented Generation microservice. "
        "Upload documents via **POST /upload**, then query them via **POST /ask**."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ─────────────────────────────────────────────────────────
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(RuntimeError, runtime_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(router, tags=["RAG"])


@app.get("/", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "service": "Mini-RAG Service",
        "chunks_indexed": vector_store.count,
    }
