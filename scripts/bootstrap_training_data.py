from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import requests


def _fetch_capabilities(base_url: str) -> dict:
    try:
        response = requests.get(f"{base_url.rstrip('/')}/v1/meta/capabilities", timeout=30)
    except requests.RequestException as exc:
        raise SystemExit(
            f"Could not reach API capabilities endpoint at {base_url.rstrip('/')}/v1/meta/capabilities: {exc}"
        ) from exc
    response.raise_for_status()
    return response.json()


def _fetch_candidate_page(
    base_url: str,
    limit: int,
    offset: int,
    min_completeness_score: float,
    include_reused: bool,
) -> dict:
    try:
        response = requests.get(
            f"{base_url.rstrip('/')}/v1/meta/live-feature-candidates",
            params={
                "limit": limit,
                "offset": offset,
                "min_completeness_score": min_completeness_score,
                "include_reused": str(include_reused).lower(),
            },
            timeout=30,
        )
    except requests.RequestException as exc:
        raise SystemExit(
            "Could not fetch live feature candidates from API: "
            f"{base_url.rstrip('/')}/v1/meta/live-feature-candidates ({exc})"
        ) from exc
    response.raise_for_status()
    return response.json()


def _build_training_frame(
    candidates: list[dict],
    expected_features: list[str],
    target_column: str = "SalePrice",
) -> pd.DataFrame:
    rows: list[dict] = []
    for item in candidates:
        feature_map = item.get("features", {})
        row = {feature_name: feature_map.get(feature_name) for feature_name in expected_features}
        row[target_column] = float(item.get("predicted_price", 0.0))
        rows.append(row)

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame

    # Drop rows that are missing any required model feature value.
    frame = frame.dropna(subset=expected_features)
    frame[target_column] = frame[target_column].astype(float)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap training data from live API feature candidates (no CSV source).",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="data/processed/live_feature_store.jsonl")
    parser.add_argument("--min-completeness-score", type=float, default=0.9)
    parser.add_argument("--include-reused", action="store_true")
    parser.add_argument("--page-size", type=int, default=200)
    parser.add_argument("--max-rows", type=int, default=5000)
    parser.add_argument("--target-column", default="SalePrice")
    args = parser.parse_args()

    capabilities = _fetch_capabilities(args.base_url)
    expected_features: list[str] = capabilities.get("model_expected_features", [])
    if not expected_features:
        raise SystemExit("API did not return model_expected_features; cannot build feature store.")

    all_items: list[dict] = []
    offset = 0
    while len(all_items) < args.max_rows:
        page = _fetch_candidate_page(
            base_url=args.base_url,
            limit=min(args.page_size, args.max_rows - len(all_items)),
            offset=offset,
            min_completeness_score=args.min_completeness_score,
            include_reused=args.include_reused,
        )
        items = page.get("items", [])
        if not items:
            break
        all_items.extend(items)
        offset += len(items)

    dataset = _build_training_frame(
        candidates=all_items,
        expected_features=expected_features,
        target_column=args.target_column,
    )
    if dataset.empty:
        raise SystemExit(
            "No valid live feature rows found. "
            "Run more live predictions or lower --min-completeness-score."
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_json(output_path, orient="records", lines=True)

    print(f"Live feature store written to: {output_path}")
    print(f"Rows: {len(dataset)}")
    print(f"Columns: {len(dataset.columns)}")
    print(f"Features: {len(expected_features)}")


if __name__ == "__main__":
    main()