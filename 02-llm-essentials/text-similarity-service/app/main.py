"""
FastAPI-приложение: семантический анализ текстов.
Единственный endpoint: POST /analyze
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services import compute_top_pairs, get_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Прогрев модели при старте — первый запрос не будет ждать загрузки."""
    logger.info("Старт приложения — загрузка ML-модели...")
    get_model()
    logger.info("Приложение готово к работе.")
    yield
    logger.info("Остановка приложения.")


app = FastAPI(
    title="Text Similarity Service",
    description="Семантический анализ текстов на основе sentence-transformers.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Единый обработчик ошибок валидации — возвращает 422 с понятным сообщением."""
    errors = [
        {
            "field": " -> ".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Ошибка валидации входных данных.", "errors": errors},
    )


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Анализ схожести текстов",
    description=(
        "Принимает список строк (минимум 2), возвращает ТОП-3 "
        "наиболее похожих пары с косинусным сходством."
    ),
)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    logger.info("Получен запрос: %d текстов", len(request.texts))

    try:
        top_pairs = compute_top_pairs(request.texts, top_n=3)
    except Exception as exc:
        logger.exception("Ошибка при обработке запроса: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при обработке текстов.",
        ) from exc

    logger.info("Запрос обработан успешно, возвращено %d пар.", len(top_pairs))
    return AnalyzeResponse(total_texts=len(request.texts), top_pairs=top_pairs)


@app.get("/health", summary="Проверка работоспособности сервиса")
async def health() -> dict:
    return {"status": "ok"}
