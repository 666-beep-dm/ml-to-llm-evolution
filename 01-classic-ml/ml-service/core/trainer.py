"""Training logic — Single Responsibility: load data, train, persist."""

import logging
import pathlib
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from core.pipeline import build_pipeline

log = logging.getLogger(__name__)

NUMERIC_FEATURES = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
]
CATEGORICAL_FEATURES = ["Geography", "Gender"]

# Map API field names (snake_case) → CSV column names (PascalCase)
RENAME_MAP = {
    "credit_score":     "CreditScore",
    "geography":        "Geography",
    "gender":           "Gender",
    "age":              "Age",
    "tenure":           "Tenure",
    "balance":          "Balance",
    "num_of_products":  "NumOfProducts",
    "has_cr_card":      "HasCrCard",
    "is_active_member": "IsActiveMember",
    "estimated_salary": "EstimatedSalary",
}


class Trainer:
    def __init__(self, model_path: str) -> None:
        self._model_path = pathlib.Path(model_path)
        self._model_path.parent.mkdir(parents=True, exist_ok=True)

    def train(self, csv_path: str, target_column: str) -> dict:
        df = self._load_csv(csv_path)

        X = df.drop(columns=[target_column])
        y = df[target_column]

        # Retain only columns the pipeline expects
        X = X[NUMERIC_FEATURES + CATEGORICAL_FEATURES]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        log.info("Building pipeline — train rows: %d", len(X_train))
        pipeline = build_pipeline(NUMERIC_FEATURES, CATEGORICAL_FEATURES)
        pipeline.fit(X_train, y_train)

        accuracy = accuracy_score(y_test, pipeline.predict(X_test))
        log.info("Validation accuracy: %.4f", accuracy)

        joblib.dump(pipeline, self._model_path)
        log.info("Model saved → %s", self._model_path)

        return {
            "message":       "Training complete.",
            "model_path":    str(self._model_path),
            "training_rows": len(X_train),
            "accuracy":      round(accuracy, 4),
        }

    @staticmethod
    def _load_csv(path: str) -> pd.DataFrame:
        p = pathlib.Path(path)
        if not p.exists():
            raise FileNotFoundError(f"CSV not found: {path}")
        df = pd.read_csv(p)
        log.info("Loaded CSV — shape: %s", df.shape)
        return df
