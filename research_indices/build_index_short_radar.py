from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("output_indices")


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


def build_short_radar(state: dict[str, Any]) -> dict[str, Any]:
    macro = state.get("macro_policy_pack", {}) or {}
    adjustments = macro.get("defensive_inverse_adjustments", {}) or {}
    rows: list[dict[str, Any]] = []
    defaults = {
        "RWM": {
            "underlying": "Russell 2000 / IWM",
            "short_thesis": "Small caps remain vulnerable when breadth is weak and real rates are restrictive.",
            "trigger": "IWM underperforms SPY while breadth and credit fail to improve.",
            "invalidation": "Broad easing impulse plus improving small-cap relative strength.",
            "max_role": "Defensive hedge only; not a long-side opportunity.",
        },
        "EUM": {
            "underlying": "Emerging Markets / EEM",
            "short_thesis": "EM remains vulnerable when USD pressure and China confidence risk rise.",
            "trigger": "UUP strengthens while EEM breaks relative support.",
            "invalidation": "USD weakens and China / EM breadth confirms upside.",
            "max_role": "Defensive hedge only; not a long-side opportunity.",
        },
        "PSQ": {
            "underlying": "Nasdaq 100 / QQQ",
            "short_thesis": "Nasdaq hedge only becomes relevant if mega-cap leadership breaks.",
            "trigger": "QQQ loses relative strength versus SPY and breadth fails.",
            "invalidation": "QQQ leadership remains intact.",
            "max_role": "Crash / drawdown hedge only; not a base-case allocation.",
        },
    }
    for proxy, template in defaults.items():
        adj = adjustments.get(proxy, {}) or {}
        readiness = adj.get("readiness", "inactive")
        rows.append({
            "candidate": proxy,
            "underlying": adj.get("underlying", template["underlying"]),
            "readiness": readiness,
            "short_thesis": template["short_thesis"],
            "trigger": template["trigger"],
            "invalidation": template["invalidation"],
            "regime_condition": adj.get("reason", "Requires confirmed breakdown before use."),
            "portfolio_use": "defensive_inverse_only",
            "max_role": template["max_role"],
            "client_status": "Watchlist" if readiness == "watchlist" else "Inactive / monitor only",
        })
    return {
        "generated_at_utc": state.get("generated_at_utc"),
        "report_token": state.get("report_token"),
        "report_date": state.get("report_date"),
        "separation_rule": "These are defensive / inverse candidates only and must not appear in the long-side opportunity board.",
        "rows": rows,
    }


def main() -> None:
    state_path = _latest_runtime_state()
    if state_path is None:
        raise RuntimeError("No runtime state found. Run runtime_indices.build_index_report_state first.")
    state = _read_json(state_path)
    payload = build_short_radar(state)
    token = payload.get("report_token") or "unknown"
    out_path = OUTPUT_DIR / "research" / f"index_short_radar_{token}.json"
    _write_json(out_path, payload)
    print(f"INDEX_SHORT_RADAR_OK | token={token} | rows={len(payload['rows'])} | output={out_path.name}")


if __name__ == "__main__":
    main()
