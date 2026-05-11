from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pricing_indices.catalog import BY_EXPOSURE_ID

OUTPUT_DIR = Path("output_indices")
DUEL_TARGETS = {
    "us_large_cap": ["us_tech_leadership", "europe_large_cap", "japan_equities"],
    "us_tech_leadership": ["us_large_cap", "us_small_cap"],
    "us_small_cap": ["us_large_cap"],
    "em_broad": ["india_large_cap", "china_large_cap", "us_large_cap"],
    "europe_large_cap": ["germany_cyclicals", "uk_large_cap", "switzerland_large_cap"],
    "japan_equities": ["europe_large_cap", "us_large_cap"],
}
DEFENSIVE_PROXY_MAP = {
    "us_small_cap": "RWM",
    "em_broad": "EUM",
    "us_tech_leadership": "PSQ",
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def _latest_runtime_state() -> Path | None:
    hits = sorted((OUTPUT_DIR / "runtime").glob("index_report_state_*.json")) if (OUTPUT_DIR / "runtime").exists() else []
    return hits[-1] if hits else None


def _rows_by_exposure(rs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row.get("exposure_id")): row for row in rs.get("rows", []) or [] if row.get("exposure_id")}


def _num(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _edge(candidate: dict[str, Any], current: dict[str, Any], key: str) -> float | None:
    c = _num(candidate.get(key))
    h = _num(current.get(key))
    if c is None or h is None:
        return None
    return round((c - h) * 100.0, 2)


def _decision(edge_20d: float | None, edge_60d: float | None, regime_fit: str, is_defensive: bool) -> str:
    if edge_20d is None or edge_60d is None:
        return "Not decision-grade this week — relative-strength proof incomplete."
    if is_defensive:
        if regime_fit == "watchlist" and (edge_20d > 0 or edge_60d > 0):
            return "Defensive hedge watch — only usable if trigger confirms."
        return "Defensive only; not a base-case allocation."
    if edge_60d >= 3.0:
        return "Alternative improving; keep replacement duel active."
    if edge_20d > 0 and edge_60d <= 0:
        return "Early improvement only; wait for 60d confirmation."
    return "Current exposure still leads; no replacement."


def build_duels(state: dict[str, Any]) -> dict[str, Any]:
    rs_rows = _rows_by_exposure(state.get("relative_strength", {}))
    positions = state.get("positions", []) or []
    held_ids = [str(pos.get("exposure_id")) for pos in positions if pos.get("exposure_id")]
    macro = state.get("macro_policy_pack", {}) or {}
    defensive = macro.get("defensive_inverse_adjustments", {}) or {}

    rows: list[dict[str, Any]] = []
    for exposure_id in held_ids:
        current_rs = rs_rows.get(exposure_id, {})
        current_catalog = BY_EXPOSURE_ID.get(exposure_id, {})
        for alt_id in DUEL_TARGETS.get(exposure_id, []):
            alt_rs = rs_rows.get(alt_id, {})
            alt_catalog = BY_EXPOSURE_ID.get(alt_id, {})
            edge_20d = _edge(alt_rs, current_rs, "return_20d")
            edge_60d = _edge(alt_rs, current_rs, "return_60d")
            rows.append({
                "current_exposure_id": exposure_id,
                "current_name": current_catalog.get("display_name", exposure_id),
                "current_proxy": current_catalog.get("primary_proxy"),
                "alternative_exposure_id": alt_id,
                "alternative_name": alt_catalog.get("display_name", alt_id),
                "alternative_proxy": alt_catalog.get("primary_proxy"),
                "duel_type": "long_alternative",
                "edge_20d_pct": edge_20d,
                "edge_60d_pct": edge_60d,
                "regime_fit": "candidate" if edge_60d is not None and edge_60d > 0 else "watchlist",
                "decision": _decision(edge_20d, edge_60d, "candidate", False),
                "required_trigger": "Needs positive 60d edge plus portfolio-fit improvement before funding.",
            })
        if exposure_id in DEFENSIVE_PROXY_MAP:
            proxy = DEFENSIVE_PROXY_MAP[exposure_id]
            readiness = (defensive.get(proxy) or {}).get("readiness", "inactive")
            rows.append({
                "current_exposure_id": exposure_id,
                "current_name": current_catalog.get("display_name", exposure_id),
                "current_proxy": current_catalog.get("primary_proxy"),
                "alternative_exposure_id": f"inverse_{proxy.lower()}",
                "alternative_name": f"Inverse hedge for {current_catalog.get('display_name', exposure_id)}",
                "alternative_proxy": proxy,
                "duel_type": "defensive_inverse",
                "edge_20d_pct": None,
                "edge_60d_pct": None,
                "regime_fit": readiness,
                "decision": _decision(None, None, readiness, True),
                "required_trigger": (defensive.get(proxy) or {}).get("reason", "Requires confirmed breakdown before use."),
            })

    return {
        "generated_at_utc": state.get("generated_at_utc"),
        "report_token": state.get("report_token"),
        "report_date": state.get("report_date"),
        "methodology": "Direct alternative duels compare current implemented exposures against long alternatives; defensive/inverse rows remain separate from the long board.",
        "rows": rows,
    }


def main() -> None:
    state_path = _latest_runtime_state()
    if state_path is None:
        raise RuntimeError("No runtime state found. Run runtime_indices.build_index_report_state first.")
    state = _read_json(state_path)
    payload = build_duels(state)
    token = payload.get("report_token") or "unknown"
    out_path = OUTPUT_DIR / "research" / f"index_alternative_duels_{token}.json"
    _write_json(out_path, payload)
    print(f"INDEX_ALTERNATIVE_DUELS_OK | token={token} | rows={len(payload['rows'])} | output={out_path.name}")


if __name__ == "__main__":
    main()
