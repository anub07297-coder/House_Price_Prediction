from __future__ import annotations

import glob
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


EXCLUDED_FEATURES = {
    "NEXT OPEN HOUSE START TIME",
    "NEXT OPEN HOUSE END TIME",
    "SOLD DATE",
    "SOLD_DATE",
    "URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)",
    "SOURCE",
    "MLS#",
    "FAVORITE",
    "INTERESTED",
    "ADDRESS",
}


def _drop_excluded_features(df: pd.DataFrame) -> pd.DataFrame:
    columns_to_drop = [col for col in EXCLUDED_FEATURES if col in df.columns]
    if not columns_to_drop:
        return df
    return df.drop(columns=columns_to_drop)


def load_dataset(path: Path) -> pd.DataFrame:
    path_str = str(path)

    # Support glob patterns like data/raw/HousingPriceUSA/*.csv
    if any(ch in path_str for ch in "*?[]"):
        matched_files = sorted(Path(p) for p in glob.glob(path_str))
        if not matched_files:
            raise FileNotFoundError(
                f"Dataset pattern matched no files at {path}. Update RAW_DATA_PATH if needed."
            )
        frames = [load_dataset(file_path) for file_path in matched_files]
        return _drop_excluded_features(pd.concat(frames, ignore_index=True))

    # Support directories by loading all CSV files within the folder.
    if path.is_dir():
        csv_files = sorted(path.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(
                f"No CSV files found in directory {path}. Update RAW_DATA_PATH if needed."
            )
        frames = [pd.read_csv(file_path) for file_path in csv_files]
        return _drop_excluded_features(pd.concat(frames, ignore_index=True))

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. Add your CSV and update RAW_DATA_PATH if needed."
        )
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _drop_excluded_features(pd.read_csv(path))
    if suffix in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True)
    if suffix == ".json":
        return pd.read_json(path)
    raise ValueError(
        f"Unsupported dataset file type '{suffix}'. Supported: .csv, .jsonl, .ndjson, .json"
    )


def split_features_target(df: pd.DataFrame, target_column: str) -> tuple[pd.DataFrame, pd.Series]:
    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' not found in dataset.")

    y_numeric = pd.to_numeric(df[target_column], errors="coerce")
    valid_target_mask = y_numeric.notna()
    if not valid_target_mask.any():
        raise ValueError(
            f"Target column '{target_column}' has no valid numeric values after cleaning."
        )

    x = df.loc[valid_target_mask].drop(columns=[target_column])
    y = y_numeric.loc[valid_target_mask]
    return x, y


def make_train_test_split(
    x: pd.DataFrame,
    y: pd.Series,
    test_size: float,
    random_state: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    return train_test_split(x, y, test_size=test_size, random_state=random_state)
