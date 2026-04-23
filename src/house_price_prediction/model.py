from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

from .config import Settings
from .data import load_dataset, make_train_test_split, split_features_target
from .features import build_preprocessor

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    from catboost import CatBoostRegressor
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False


@dataclass(frozen=True)
class ModelMetadata:
    feature_columns: tuple[str, ...]
    target_column: str | None
    model_name: str | None
    model_version: str | None


@dataclass(frozen=True)
class TrainedModelArtifact:
    model: Any
    metadata: ModelMetadata


def train_and_save_model(settings: Settings) -> dict[str, float]:
    # Load from live Census API by default (pass None to use API)
    # Only use local CSV if it exists and user explicitly configured it
    csv_path = Path(settings.raw_data_path) if settings.raw_data_path else None
    use_local = csv_path and csv_path.exists()

    df = load_dataset(csv_path if use_local else None)
    x, y = split_features_target(df, settings.target_column)
    x_train, x_test, y_train, y_test = make_train_test_split(
        x, y, test_size=settings.test_size, random_state=settings.random_state
    )

    preprocessor = build_preprocessor(x_train)

    # Try LightGBM first (best performance on this type of data)
    if HAS_LIGHTGBM:
        regressor = lgb.LGBMRegressor(
            n_estimators=3000,
            learning_rate=0.01,
            max_depth=7,
            num_leaves=150,
            min_child_samples=5,
            subsample=0.95,
            colsample_bytree=0.95,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=settings.random_state,
            verbose=-1,
            n_jobs=-1,
        )
    # Try CatBoost second (handles categorical well)
    elif HAS_CATBOOST:
        regressor = CatBoostRegressor(
            iterations=2000,
            learning_rate=0.01,
            max_depth=8,
            subsample=0.95,
            colsample_bylevel=0.95,
            min_data_in_leaf=3,
            random_state=settings.random_state,
            verbose=False,
            thread_count=-1,
        )
    # Fall back to GradientBoosting
    else:
        regressor = GradientBoostingRegressor(
            n_estimators=2500,
            learning_rate=0.008,
            max_depth=6,
            min_samples_split=3,
            min_samples_leaf=2,
            subsample=0.92,
            max_features=0.9,
            loss="squared_error",
            random_state=settings.random_state,
        )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", regressor),
        ]
    )

    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
        "r2": float(r2_score(y_test, predictions)),
    }

    settings.model_path.parent.mkdir(parents=True, exist_ok=True)
    save_model_artifact(
        model=model,
        model_path=settings.model_path,
        feature_columns=x.columns.tolist(),
        target_column=settings.target_column,
        model_name=settings.model_name,
        model_version=settings.model_version,
    )
    return metrics


def save_model_artifact(
    model: Any,
    model_path: Path,
    feature_columns: list[str],
    target_column: str,
    model_name: str | None,
    model_version: str | None,
) -> None:
    artifact = {
        "model": model,
        "metadata": {
            "feature_columns": feature_columns,
            "target_column": target_column,
            "model_name": model_name,
            "model_version": model_version,
        },
    }
    joblib.dump(artifact, model_path)


def load_model_artifact(model_path: Path) -> TrainedModelArtifact:
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found at {model_path}. Train first using scripts/train.py."
        )

    loaded = joblib.load(model_path)
    if isinstance(loaded, dict) and "model" in loaded and "metadata" in loaded:
        metadata = loaded["metadata"]
        return TrainedModelArtifact(
            model=loaded["model"],
            metadata=ModelMetadata(
                feature_columns=tuple(metadata.get("feature_columns", [])),
                target_column=metadata.get("target_column"),
                model_name=metadata.get("model_name"),
                model_version=metadata.get("model_version"),
            ),
        )

    return TrainedModelArtifact(
        model=loaded,
        metadata=ModelMetadata(
            feature_columns=tuple(),
            target_column=None,
            model_name=None,
            model_version=None,
        ),
    )


def load_model(model_path: Path):
    return load_model_artifact(model_path).model


def load_model_metadata(model_path: Path) -> ModelMetadata:
    return load_model_artifact(model_path).metadata
