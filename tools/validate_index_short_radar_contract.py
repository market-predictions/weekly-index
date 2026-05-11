from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("output_indices")
REQUIRED_FIELDS = ["candidate", "underlying", "short_thesis", "trigger", "invalidation", "portfolio_use", "max_role"]


def _latest_short_radar() -> Path | None:
    hits = sorted((OUTPUT_DIR / "research").glob("index_short_radar_*.json")) if (OUTPUT_DIR / "research").exists() else []
    return hits[-1] if hits else None


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> None:
    path = _latest_short_radar()
    if path is None:
        raise RuntimeError("Index short radar contract failed: no index_short_radar_*.json artifact found.")
    payload = _read_json(path)
    rows = payload.get("rows", []) or []
    if not rows:
        raise RuntimeError(f"Index short radar contract failed: no rows in {path.name}.")
    for row in rows:
        missing = [field for field in REQUIRED_FIELDS if not str(row.get(field) or "").strip()]
        if missing:
            raise RuntimeError(f"Index short radar contract failed: {row.get('candidate')} missing {', '.join(missing)}")
        if str(row.get("portfolio_use")) != "defensive_inverse_only":
            raise RuntimeError(f"Index short radar contract failed: {row.get('candidate')} is not marked defensive_inverse_only.")
    print(f"INDEX_SHORT_RADAR_CONTRACT_OK | file={path.name} | rows={len(rows)}")


if __name__ == "__main__":
    validate()
