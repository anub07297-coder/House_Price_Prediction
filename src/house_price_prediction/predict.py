from __future__ import annotations

from pathlib import Path

import pandas as pd

from .model import load_model


def predict_from_csv(model_path: Path, input_path: Path) -> pd.Series:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found at {input_path}")
    model = load_model(model_path)
    features = pd.read_csv(input_path)
    predictions = model.predict(features)
    return pd.Series(predictions, name="predicted_price")
