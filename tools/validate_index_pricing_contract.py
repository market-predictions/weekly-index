from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("output_indices")
REQUIRED_PRICING_MODEL = "layered_close_discovery_v1"
REQUIRED_PROVIDERS = [
    "yahoo_chart",
    "twelve_data_time_series",
    "fmp_historical_price_full",
    "alpha_vantage_daily_adjusted",
    "carry_forward_prior_valid_close",
]


def _latest_audit() -> Path | None:
    hits = sorted((OUTPUT_DIR / "pricing").glob("index_price_audit_*.json")) if (OUTPUT_DIR / "pricing").exists() else []
    return hits[-1] if hits else None


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _has_value(value: Any) -> bool:
    try:
        return value is not None and float(value) > 0
    except (TypeError, ValueError):
        return False


def validate() -> None:
    path = _latest_audit()
    if path is None:
        raise RuntimeError("Index pricing contract failed: no index_price_audit_*.json found.")
    audit = _read_json(path)
    rows = audit.get("positions", []) or []
    if not rows:
        raise RuntimeError(f"Index pricing contract failed: no positions in {path.name}.")

    model = audit.get("pricing_model")
    if model != REQUIRED_PRICING_MODEL:
        raise RuntimeError(
            f"Index pricing contract failed: expected {REQUIRED_PRICING_MODEL}, found {model or 'missing'} in {path.name}."
        )
    provider_order = audit.get("provider_order") or []
    missing_providers = [provider for provider in REQUIRED_PROVIDERS if provider not in provider_order]
    if missing_providers:
        raise RuntimeError(
            "Index pricing contract failed: layered provider order incomplete: " + ", ".join(missing_providers)
        )

    missing_proxy = []
    missing_benchmark = []
    missing_source = []
    missing_performance = []
    carried_proxy = []
    for row in rows:
        exposure = row.get("exposure_id") or row.get("display_name") or "unknown"
        if not row.get("primary_proxy"):
            missing_proxy.append(str(exposure))
        if not row.get("benchmark_symbol"):
            missing_benchmark.append(str(exposure))
        if not _has_value(row.get("proxy_close")):
            missing_proxy.append(f"{exposure}:proxy_close")
        if not row.get("proxy_source"):
            missing_source.append(f"{exposure}:proxy_source")
        if not row.get("benchmark_source"):
            missing_source.append(f"{exposure}:benchmark_source")
        if str(row.get("proxy_status") or "").startswith("carried_forward"):
            carried_proxy.append(str(exposure))
        performance = row.get("performance") or {}
        for field in ["one_week_return_pct", "one_month_return_pct", "three_month_return_pct", "since_entry_return_pct"]:
            if field not in performance:
                missing_performance.append(f"{exposure}:{field}")
    if missing_proxy:
        raise RuntimeError("Index pricing contract failed: proxy pricing incomplete for " + ", ".join(missing_proxy))
    if missing_benchmark:
        raise RuntimeError("Index pricing contract failed: benchmark symbols missing for " + ", ".join(missing_benchmark))
    if missing_source:
        raise RuntimeError("Index pricing contract failed: price source diagnostics incomplete for " + ", ".join(missing_source))
    if missing_performance:
        raise RuntimeError("Index pricing contract failed: performance metrics incomplete for " + ", ".join(missing_performance))

    print(
        f"INDEX_PRICING_CONTRACT_OK | audit={path.name} | positions={len(rows)} | "
        f"requested_close={audit.get('requested_close_date')} | pricing_model={model} | carried_proxy={len(carried_proxy)}"
    )


if __name__ == "__main__":
    validate()
