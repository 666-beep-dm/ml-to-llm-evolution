"""
Точка входа FastAPI-приложения.
lifespan управляет прогревом модели и фоновым воркером.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.router import router
from src.api.dependencies import get_search_service
from src.core.embedder import _load_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Запуск Semantic Search Engine ===")
    _load_model()                          # прогрев модели
    service = get_search_service()
    await service.start()                  # фоновый воркер
    logger.info("=== Сервис готов к работе ===")
    yield
    logger.info("=== Остановка сервиса ===")
    await service.stop()


app = FastAPI(
    title="Semantic Search Engine",
    description="Семантический поиск на FastAPI + FAISS + sentence-transformers.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {"field": " -> ".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Ошибка валидации.", "errors": errors},
    )


app.include_router(router)


@app.get("/health", tags=["System"])
async def health() -> dict:
    service = get_search_service()
    return {"status": "ok", "indexed_documents": service._repo.count()}
