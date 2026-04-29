from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import requests


def fetch_page(
    base_url: str,
    limit: int,
    offset: int,
    min_completeness_score: float,
    include_reused: bool,
) -> dict:
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
    response.raise_for_status()
    return response.json()


def flatten_items(items: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for item in items:
        normalized_address = item.get("normalized_address", {})
        features = item.get("features", {})
        row = {
            "prediction_id": item.get("prediction_id"),
            "request_id": item.get("request_id"),
            "submitted_at": item.get("submitted_at"),
            "generated_at": item.get("generated_at"),
            "predicted_price": item.get("predicted_price"),
            "completeness_score": item.get("completeness_score"),
            "was_reused": item.get("was_reused"),
            "model_name": item.get("model_name"),
            "model_version": item.get("model_version"),
            "selected_feature_policy_name": item.get("selected_feature_policy_name"),
            "selected_feature_policy_version": item.get("selected_feature_policy_version"),
            "feature_source": item.get("feature_source"),
            "provider_name": item.get("provider_name"),
            "address_state": normalized_address.get("state"),
            "address_city": normalized_address.get("city"),
            "address_postal_code": normalized_address.get("postal_code"),
            "address_country": normalized_address.get("country"),
            "address_latitude": normalized_address.get("latitude"),
            "address_longitude": normalized_address.get("longitude"),
        }
        for key, value in features.items():
            row[f"feature__{key}"] = value
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export live feature candidates from API traffic into a flat CSV.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="data/processed/live_feature_candidates.csv")
    parser.add_argument("--min-completeness-score", type=float, default=0.8)
    parser.add_argument("--include-reused", action="store_true")
    parser.add_argument("--page-size", type=int, default=200)
    parser.add_argument("--max-rows", type=int, default=5000)
    args = parser.parse_args()

    all_items: list[dict] = []
    offset = 0
    while len(all_items) < args.max_rows:
        page = fetch_page(
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

    rows = flatten_items(all_items)
    df = pd.DataFrame(rows)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Exported {len(df)} rows to {output_path}")
    print(f"Columns: {len(df.columns)}")


if __name__ == "__main__":
    main()
