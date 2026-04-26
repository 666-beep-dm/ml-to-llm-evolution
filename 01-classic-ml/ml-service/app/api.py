"""FastAPI route definitions."""

import logging
from fastapi import FastAPI
from app.schemas import PredictRequest, PredictResponse, TrainRequest, TrainResponse
from app.exceptions import (
    register_exception_handlers,
    PredictionError,
    TrainingError,
)
from core.predictor import Predictor
from core.trainer import Trainer

log = logging.getLogger(__name__)

MODEL_PATH = "models/pipeline.joblib"


def create_app() -> FastAPI:
    app = FastAPI(
        title="ML Churn Prediction Service",
        version="1.0.0",
        description="Production-ready ML API for Bank Churn classification.",
    )
    register_exception_handlers(app)
    _register_routes(app)
    return app


def _register_routes(app: FastAPI) -> None:

    @app.get("/health", tags=["Meta"])
    async def health():
        return {"status": "ok"}

    @app.post("/predict", response_model=PredictResponse, tags=["Inference"])
    async def predict(request: PredictRequest):
        """Run inference on a single customer record."""
        log.info("POST /predict — input: %s", request.features.model_dump())
        try:
            predictor = Predictor(MODEL_PATH)
            result = predictor.predict(request.features.model_dump())
        except Exception as exc:
            raise PredictionError(f"Inference failed: {exc}") from exc

        log.info("POST /predict — result: %s", result)
        return result

    @app.post("/train", response_model=TrainResponse, tags=["Training"])
    async def train(request: TrainRequest):
        """Trigger training pipeline on a CSV and persist the model."""
        log.info(
            "POST /train — csv: %s | target: %s",
            request.csv_path,
            request.target_column,
        )
        try:
            trainer = Trainer(MODEL_PATH)
            result = trainer.train(request.csv_path, request.target_column)
        except Exception as exc:
            raise TrainingError(f"Training failed: {exc}") from exc

        log.info("POST /train — complete: %s", result)
        return result
