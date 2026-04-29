"""
Train model using prepared splits from the training pipeline.
Loads train.jsonl, val.jsonl, and test.jsonl from data/processed/training_pipeline/splits/
"""
import warnings
from pathlib import Path
import pickle

import numpy as np
import joblib
from lightgbm import LGBMRegressor
from sklearn.compose import TransformedTargetRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
import pandas as pd

from house_price_prediction.config import load_settings
from house_price_prediction.features import build_preprocessor


def load_splits(splits_dir: Path = Path("data/processed/training_pipeline/splits")):
    """Load train, validation, and test splits from JSONL files."""
    train_path = splits_dir / "train.jsonl"
    val_path = splits_dir / "val.jsonl"
    test_path = splits_dir / "test.jsonl"

    if not all(p.exists() for p in [train_path, val_path, test_path]):
        raise FileNotFoundError(
            f"Training splits not found in {splits_dir}. "
            "Run scripts/build_training_pipeline.py first."
        )

    # Load JSONL files
    train_df = pd.read_json(train_path, lines=True)
    val_df = pd.read_json(val_path, lines=True)
    test_df = pd.read_json(test_path, lines=True)

    return train_df, val_df, test_df


def prepare_data(train_df, val_df, test_df, target_column: str = "SalePrice"):
    """Prepare features and targets from loaded splits."""
    # Extract target and features
    x_train = train_df.drop(columns=[target_column])
    y_train = train_df[target_column]

    x_val = val_df.drop(columns=[target_column])
    y_val = val_df[target_column]

    x_test = test_df.drop(columns=[target_column])
    y_test = test_df[target_column]

    return x_train, y_train, x_val, y_val, x_test, y_test


def train_and_save_model_from_splits(settings) -> dict[str, float]:
    """Train model using prepared pipeline splits."""
    print("[train] Loading pipeline splits...")
    train_df, val_df, test_df = load_splits()
    
    print(f"[train] Loaded: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")
    print(f"[train] Features: {list(train_df.columns)}")

    # Prepare data
    x_train, y_train, x_val, y_val, x_test, y_test = prepare_data(
        train_df, val_df, test_df, target_column="SalePrice"
    )

    print(f"[train] Building preprocessor on {len(x_train)} training samples...")
    preprocessor = build_preprocessor(x_train)

    print("[train] Creating LGBMRegressor model...")
    regressor = LGBMRegressor(
        objective="fair",
        n_estimators=1000,
        learning_rate=0.02,
        num_leaves=95,
        min_child_samples=8,
        subsample=0.8,
        colsample_bytree=0.7,
        reg_alpha=0.01,
        reg_lambda=8.0,
        n_jobs=-1,
        random_state=settings.random_state,
        verbose=-1,
    )

    transformed_regressor = TransformedTargetRegressor(
        regressor=regressor,
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=False,
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", transformed_regressor),
        ]
    )

    print("[train] Training model on training set...")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(x_train, y_train)
        
        print("[train] Evaluating on validation set...")
        val_predictions = model.predict(x_val)
        
        print("[train] Evaluating on test set...")
        test_predictions = model.predict(x_test)

    # Compute metrics on test set
    print("[train] Computing metrics on test set...")
    non_zero_mask = y_test != 0
    if non_zero_mask.any():
        mape = float(
            mean_absolute_percentage_error(
                y_test[non_zero_mask], test_predictions[non_zero_mask]
            )
            * 100
        )
    else:
        mape = float("nan")

    metrics = {
        "mae": float(mean_absolute_error(y_test, test_predictions)),
        "mape": mape,
        "rmse": float(np.sqrt(mean_squared_error(y_test, test_predictions))),
        "r2": float(r2_score(y_test, test_predictions)),
    }

    # Also compute validation metrics for monitoring
    val_non_zero_mask = y_val != 0
    if val_non_zero_mask.any():
        val_mape = float(
            mean_absolute_percentage_error(
                y_val[val_non_zero_mask], val_predictions[val_non_zero_mask]
            )
            * 100
        )
    else:
        val_mape = float("nan")

    val_metrics = {
        "val_mae": float(mean_absolute_error(y_val, val_predictions)),
        "val_mape": val_mape,
        "val_rmse": float(np.sqrt(mean_squared_error(y_val, val_predictions))),
        "val_r2": float(r2_score(y_val, val_predictions)),
    }

    metrics.update(val_metrics)

    # Save model
    print(f"[train] Saving model to {settings.model_path}...")
    settings.model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings.model_path, 'wb') as f:
        pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)

    return metrics


if __name__ == "__main__":
    settings = load_settings()
    metrics = train_and_save_model_from_splits(settings)

    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"Model saved to: {settings.model_path}")
    print("\nMetrics:")
    print("-" * 60)
    for name, value in sorted(metrics.items()):
        if isinstance(value, float):
            if "mape" in name.lower():
                print(f"  {name:.<40} {value:>10.2f}%")
            else:
                print(f"  {name:.<40} ${value:>10,.2f}" if name == "mae" or name == "val_mae" else f"  {name:.<40} {value:>10.4f}")
        else:
            print(f"  {name:.<40} {value:>10}")
    print("="*60)
