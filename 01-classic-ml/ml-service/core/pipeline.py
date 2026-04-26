"""
sklearn Pipeline factory.

Follows the Open/Closed principle — extend MODELS or add transformers
without modifying existing logic.
"""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier
from typing import Literal

ModelType = Literal["xgboost", "random_forest"]


def build_pipeline(
    numeric_features:     list[str],
    categorical_features: list[str],
    model_type:           ModelType = "xgboost",
    random_state:         int = 42,
) -> Pipeline:
    """
    Construct a full sklearn Pipeline with:
      - Numeric branch     : median imputation → StandardScaler
      - Categorical branch : most-frequent imputation → OneHotEncoder
      - Estimator          : XGBClassifier or RandomForestClassifier
    """
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_transformer,     numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ])

    estimator = _get_estimator(model_type, random_state)

    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier",   estimator),
    ])


def _get_estimator(model_type: ModelType, random_state: int):
    if model_type == "xgboost":
        return XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            eval_metric="logloss",
            random_state=random_state,
        )
    if model_type == "random_forest":
        from sklearn.ensemble import RandomForestClassifier
        return RandomForestClassifier(n_estimators=200, random_state=random_state)

    raise ValueError(
        f"Unknown model_type: '{model_type}'. Choose 'xgboost' or 'random_forest'."
    )
