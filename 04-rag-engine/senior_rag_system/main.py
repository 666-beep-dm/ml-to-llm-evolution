"""
Application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.routers import ingest, query, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting {} …", settings.app_name)
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Production-ready RAG system with ChromaDB, Redis semantic cache, and Cross-Encoder reranking.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(health.router)


@app.get("/", include_in_schema=False)
async def root():
    return {"message": f"Welcome to {settings.app_name}. Docs at /docs"}
