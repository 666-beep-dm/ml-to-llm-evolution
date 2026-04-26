"""
Middle-level ML pipeline for Wine Quality classification.
"""

import logging
import sys
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

RANDOM_STATE = 42
TEST_SIZE     = 0.20

MODELS: dict[str, Any] = {
    "LogisticRegression": LogisticRegression(
        max_iter=1_000, random_state=RANDOM_STATE
    ),
    "RandomForestClassifier": RandomForestClassifier(
        n_estimators=100, random_state=RANDOM_STATE
    ),
}

# ── Data ──────────────────────────────────────────────────────────────────────

@dataclass
class Dataset:
    X_train: np.ndarray
    X_test:  np.ndarray
    y_train: np.ndarray
    y_test:  np.ndarray
    feature_names: list[str] = field(default_factory=list)


def load_and_split() -> Dataset:
    """Load Wine dataset and return a train/test split."""
    log.info("Loading Wine dataset …")
    bunch = load_wine(as_frame=False)
    X, y = bunch.data, bunch.target
    log.info("Samples: %d | Features: %d | Classes: %d", *X.shape, len(np.unique(y)))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    log.info("Split → train: %d | test: %d", len(X_train), len(X_test))
    return Dataset(X_train, X_test, y_train, y_test, list(bunch.feature_names))


# ── Preprocessing ─────────────────────────────────────────────────────────────

def scale_features(ds: Dataset) -> Dataset:
    """Fit StandardScaler on train, transform both splits in-place."""
    log.info("Scaling features with StandardScaler …")
    scaler = StandardScaler()
    ds.X_train = scaler.fit_transform(ds.X_train)
    ds.X_test  = scaler.transform(ds.X_test)
    return ds


# ── Training & Evaluation ─────────────────────────────────────────────────────

@dataclass
class ModelResult:
    name:      str
    accuracy:  float
    precision: float
    recall:    float


def evaluate(name: str, model: Any, ds: Dataset) -> ModelResult:
    """Train a model and return evaluation metrics."""
    log.info("Training %s …", name)
    try:
        model.fit(ds.X_train, ds.y_train)
    except Exception as exc:
        log.error("Training failed for %s: %s", name, exc)
        raise

    y_pred = model.predict(ds.X_test)
    result = ModelResult(
        name      = name,
        accuracy  = accuracy_score(ds.y_test, y_pred),
        precision = precision_score(ds.y_test, y_pred, average="macro", zero_division=0),
        recall    = recall_score(ds.y_test, y_pred, average="macro", zero_division=0),
    )
    log.info(
        "%s → Acc: %.4f | Prec: %.4f | Rec: %.4f",
        name, result.accuracy, result.precision, result.recall,
    )
    return result


def run_pipeline() -> None:
    """End-to-end pipeline entry point."""
    log.info("=" * 55)
    log.info("ML PIPELINE START")
    log.info("=" * 55)

    ds = load_and_split()
    ds = scale_features(ds)

    results: list[ModelResult] = []
    for name, model in MODELS.items():
        results.append(evaluate(name, model, ds))

    # ── Summary table ──────────────────────────────────────────────────────
    df = pd.DataFrame([vars(r) for r in results]).set_index("name")
    df.columns = ["Accuracy", "Precision (macro)", "Recall (macro)"]
    df = df.sort_values("Accuracy", ascending=False)

    log.info("\n\n%s\n", df.to_string(float_format="{:.4f}".format))

    best = df.index[0]
    log.info("Best model: %s (Accuracy = %.4f)", best, df.loc[best, "Accuracy"])
    log.info("=" * 55)
    log.info("PIPELINE COMPLETE")
    log.info("=" * 55)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as exc:
        log.critical("Pipeline aborted: %s", exc, exc_info=True)
        sys.exit(1)