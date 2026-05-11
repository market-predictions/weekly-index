from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("output_indices")


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
    missing_proxy = []
    missing_benchmark = []
    for row in rows:
        exposure = row.get("exposure_id") or row.get("display_name") or "unknown"
        if not row.get("primary_proxy"):
            missing_proxy.append(str(exposure))
        if not row.get("benchmark_symbol"):
            missing_benchmark.append(str(exposure))
        if not _has_value(row.get("proxy_close")):
            missing_proxy.append(f"{exposure}:proxy_close")
    if missing_proxy:
        raise RuntimeError("Index pricing contract failed: proxy pricing incomplete for " + ", ".join(missing_proxy))
    if missing_benchmark:
        raise RuntimeError("Index pricing contract failed: benchmark symbols missing for " + ", ".join(missing_benchmark))
    print(f"INDEX_PRICING_CONTRACT_OK | audit={path.name} | positions={len(rows)} | requested_close={audit.get('requested_close_date')}")


if __name__ == "__main__":
    validate()
