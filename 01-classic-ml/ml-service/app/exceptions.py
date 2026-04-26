"""Custom exceptions and FastAPI exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

log = logging.getLogger(__name__)


class ModelNotFoundError(Exception):
    """Raised when no trained model artifact exists on disk."""


class PredictionError(Exception):
    """Raised when inference fails due to malformed input."""


class TrainingError(Exception):
    """Raised when the training pipeline fails."""


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(ModelNotFoundError)
    async def model_not_found_handler(request: Request, exc: ModelNotFoundError):
        log.error("ModelNotFoundError: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"detail": str(exc), "error": "MODEL_NOT_FOUND"},
        )

    @app.exception_handler(PredictionError)
    async def prediction_error_handler(request: Request, exc: PredictionError):
        log.error("PredictionError: %s", exc)
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc), "error": "PREDICTION_FAILED"},
        )

    @app.exception_handler(TrainingError)
    async def training_error_handler(request: Request, exc: TrainingError):
        log.error("TrainingError: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "error": "TRAINING_FAILED"},
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        log.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error.", "error": "INTERNAL_ERROR"},
        )
