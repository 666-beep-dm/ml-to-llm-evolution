"""
Application factory — wires all dependencies, mounts routers.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import RAGException
from app.api.middleware import ObservabilityMiddleware, rag_exception_handler, unhandled_exception_handler
from app.api.routes import ingest, query, health, metrics
from app.infrastructure.cache import create_cache
from app.infrastructure.vector_store import QdrantVectorStore
from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
from app.services.rag_service import RAGService

configure_logging()
logger = get_logger("startup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    logger.info("service.starting", name=s.service_name, env=s.environment)

    # Infrastructure
    cache = await create_cache()
    vector_store = QdrantVectorStore()
    await vector_store.init_collection()

    # Services
    embedder = EmbeddingService(cache)
    embedder.load()
    reranker = RerankerService()
    reranker.load()
    rag = RAGService(vector_store, embedder, reranker, cache)

    # Attach to app state for dependency injection
    app.state.cache = cache
    app.state.vector_store = vector_store
    app.state.rag_service = rag

    logger.info("service.ready", chunks=await vector_store.count())
    yield
    logger.info("service.shutdown")


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(
        title="Production-Ready RAG Service",
        description=(
            "Senior-level RAG microservice with two-stage retrieval, "
            "reranking, streaming, caching, and full observability."
        ),
        version="3.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Middleware (order matters: outermost first)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.add_middleware(ObservabilityMiddleware)

    # Exception handlers
    app.add_exception_handler(RAGException, rag_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(ingest.router, tags=["Ingestion"])
    app.include_router(query.router, tags=["Query"])
    app.include_router(metrics.router)

    return app


app = create_app()
