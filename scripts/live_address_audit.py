from __future__ import annotations

import argparse
import json
from typing import Any

import requests


def _request(
    method: str,
    base_url: str,
    path: str,
    payload: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> tuple[int | None, dict[str, Any], str]:
    target = f"{base_url.rstrip('/')}{path}"
    try:
        response = requests.request(
            method=method,
            url=target,
            json=payload,
            params=params,
            timeout=30,
        )
        try:
            body = response.json()
        except ValueError:
            body = {"raw": response.text}
        return response.status_code, body, target
    except requests.RequestException as exc:
        return None, {"error": str(exc)}, target


def _print_step(name: str, status: int | None, url: str, body: dict[str, Any]) -> None:
    print(f"\n=== {name} ===")
    print(f"URL: {url}")
    print(f"Status: {status}")
    print(json.dumps(body, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an end-to-end live address audit against the API.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--address-line-1", required=True)
    parser.add_argument("--address-line-2", default="")
    parser.add_argument("--city", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--postal-code", required=True)
    parser.add_argument("--country", default="US")
    parser.add_argument("--requested-by", default="live-audit@local")
    parser.add_argument("--skip-baseline", action="store_true")
    parser.add_argument("--skip-trace", action="store_true")
    parser.add_argument(
        "--allow-not-live-ready",
        action="store_true",
        help="Allow audit execution even when /v1/health reports live_mode_ready=false.",
    )

    args = parser.parse_args()

    address_payload: dict[str, Any] = {
        "address_line_1": args.address_line_1,
        "city": args.city,
        "state": args.state,
        "postal_code": args.postal_code,
        "country": args.country,
    }
    if args.address_line_2.strip():
        address_payload["address_line_2"] = args.address_line_2.strip()

    health_status, health_body, health_url = _request("GET", args.base_url, "/v1/health")
    _print_step("Health", health_status, health_url, health_body)

    if health_status != 200:
        raise SystemExit(f"Health check failed with status {health_status}; aborting live audit.")

    if isinstance(health_body, dict):
        live_mode_ready = bool(health_body.get("live_mode_ready", False))
        if (not live_mode_ready) and (not args.allow_not_live_ready):
            issues = health_body.get("live_mode_issues", [])
            issue_text = ", ".join(issues) if isinstance(issues, list) else str(issues)
            raise SystemExit(
                "API is not live-ready. "
                "Fix runtime mode first or re-run with --allow-not-live-ready. "
                f"Issues: {issue_text}"
            )

    norm_status, norm_body, norm_url = _request(
        "POST",
        args.base_url,
        "/v1/properties/normalize",
        payload=address_payload,
    )
    _print_step("Normalize", norm_status, norm_url, norm_body)

    if not args.skip_baseline:
        baseline_status, baseline_body, baseline_url = _request(
            "POST",
            args.base_url,
            "/v1/validation/address-baseline",
            payload=address_payload,
        )
        _print_step("Address Baseline", baseline_status, baseline_url, baseline_body)

    prediction_payload = dict(address_payload)
    if args.requested_by.strip():
        prediction_payload["requested_by"] = args.requested_by.strip()

    pred_status, pred_body, pred_url = _request(
        "POST",
        args.base_url,
        "/v1/predictions",
        payload=prediction_payload,
    )
    _print_step("Create Prediction", pred_status, pred_url, pred_body)

    prediction_id = pred_body.get("prediction_id") if isinstance(pred_body, dict) else None
    if not prediction_id:
        raise SystemExit("Prediction failed; cannot continue to detail/trace checks.")

    detail_status, detail_body, detail_url = _request(
        "GET",
        args.base_url,
        f"/v1/predictions/{prediction_id}",
    )
    _print_step("Prediction Detail", detail_status, detail_url, detail_body)

    if not args.skip_trace:
        trace_status, trace_body, trace_url = _request(
            "GET",
            args.base_url,
            f"/v1/predictions/{prediction_id}/trace",
        )
        _print_step("Prediction Trace", trace_status, trace_url, trace_body)

        events_status, events_body, events_url = _request(
            "GET",
            args.base_url,
            f"/v1/predictions/{prediction_id}/events",
            params={"limit": 50, "offset": 0, "sort": "desc"},
        )
        _print_step("Prediction Events", events_status, events_url, events_body)


if __name__ == "__main__":
    main()
