"""Inference logic — loads the persisted pipeline and runs predictions."""

import logging
import pathlib
import joblib
import pandas as pd

from app.exceptions import ModelNotFoundError
from core.trainer import RENAME_MAP, NUMERIC_FEATURES, CATEGORICAL_FEATURES

log = logging.getLogger(__name__)

LABEL_MAP = {0: "No Churn", 1: "Churn"}


class Predictor:
    def __init__(self, model_path: str) -> None:
        path = pathlib.Path(model_path)
        if not path.exists():
            raise ModelNotFoundError(
                f"No trained model found at '{model_path}'. Call POST /train first."
            )
        self._pipeline = joblib.load(path)
        log.info("Model loaded from %s", path)

    def predict(self, features: dict) -> dict:
        # snake_case → PascalCase to match training column names
        renamed = {RENAME_MAP[k]: v for k, v in features.items() if k in RENAME_MAP}
        df = pd.DataFrame([renamed])[NUMERIC_FEATURES + CATEGORICAL_FEATURES]

        prediction  = int(self._pipeline.predict(df)[0])
        probability = float(self._pipeline.predict_proba(df)[0][prediction])

        return {
            "prediction":  prediction,
            "label":       LABEL_MAP[prediction],
            "probability": round(probability, 4),
        }
