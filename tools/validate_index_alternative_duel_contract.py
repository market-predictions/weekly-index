from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("output_indices")
REQUIRED_FIELDS = ["current_exposure_id", "current_proxy", "alternative_proxy", "duel_type", "decision", "required_trigger"]


def _latest_artifact() -> Path | None:
    hits = sorted((OUTPUT_DIR / "research").glob("index_alternative_duels_*.json")) if (OUTPUT_DIR / "research").exists() else []
    return hits[-1] if hits else None


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> None:
    path = _latest_artifact()
    if path is None:
        raise RuntimeError("Index alternative duel contract failed: no index_alternative_duels_*.json artifact found.")
    payload = _read_json(path)
    rows = payload.get("rows", []) or []
    if not rows:
        raise RuntimeError(f"Index alternative duel contract failed: no rows in {path.name}.")
    long_rows = [row for row in rows if row.get("duel_type") == "long_alternative"]
    defensive_rows = [row for row in rows if row.get("duel_type") == "defensive_inverse"]
    if not long_rows:
        raise RuntimeError("Index alternative duel contract failed: no long alternative duels found.")
    for row in rows:
        missing = [field for field in REQUIRED_FIELDS if not str(row.get(field) or "").strip()]
        if missing:
            raise RuntimeError(f"Index alternative duel contract failed: row missing {', '.join(missing)}")
        if row.get("duel_type") == "defensive_inverse" and "long" in str(row.get("decision", "")).lower():
            raise RuntimeError(f"Index alternative duel contract failed: inverse row appears as long decision: {row}")
    print(f"INDEX_ALTERNATIVE_DUEL_CONTRACT_OK | file={path.name} | long_rows={len(long_rows)} | defensive_rows={len(defensive_rows)}")


if __name__ == "__main__":
    validate()
