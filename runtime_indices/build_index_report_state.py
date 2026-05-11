from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("output_indices")
RUNTIME_DIR = OUTPUT_DIR / "runtime"
REPORT_RE = re.compile(r"weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def _latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern)) if directory.exists() else []
    return files[-1] if files else None


def _latest_report_token(output_dir: Path) -> str:
    hits: list[tuple[str, int]] = []
    for path in output_dir.glob("weekly_indices_review_*.md"):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or "1")))
    if not hits:
        return datetime.utcnow().strftime("%y%m%d")
    hits.sort()
    return hits[-1][0]


def _read_scorecard(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _index_by(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = str(row.get(key) or "").strip()
        if value:
            out[value] = row
    return out


def build_state(output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    token = _latest_report_token(output_dir)
    portfolio_state_path = output_dir / "index_portfolio_state.json"
    scorecard_path = output_dir / "index_recommendation_scorecard.csv"
    macro_pack_path = output_dir / "macro" / "latest.json"
    pricing_audit_path = _latest_file(output_dir / "pricing", "index_price_audit_*.json")
    ranking_path = output_dir / f"index_candidate_ranking_{token}.json"
    coverage_path = output_dir / f"index_discovery_coverage_{token}.json"
    macro_snapshot_path = output_dir / "research" / f"index_macro_snapshot_{token}.json"
    relative_strength_path = output_dir / "research" / f"index_relative_strength_snapshot_{token}.json"

    portfolio_state = _read_json(portfolio_state_path)
    scorecard = _read_scorecard(scorecard_path)
    score_by_exposure = _index_by(scorecard, "exposure_id")
    positions = []
    for position in portfolio_state.get("positions", []) or []:
        exposure_id = str(position.get("exposure_id") or "").strip()
        merged = dict(position)
        if exposure_id in score_by_exposure:
            merged["recommendation_scorecard"] = score_by_exposure[exposure_id]
        positions.append(merged)

    runtime_state = {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "report_token": token,
        "report_date": portfolio_state.get("pricing_basis", {}).get("requested_close_date") or datetime.utcnow().date().isoformat(),
        "source_files": {
            "portfolio_state": str(portfolio_state_path) if portfolio_state_path.exists() else None,
            "scorecard": str(scorecard_path) if scorecard_path.exists() else None,
            "pricing_audit": str(pricing_audit_path) if pricing_audit_path else None,
            "macro_policy_pack": str(macro_pack_path) if macro_pack_path.exists() else None,
            "candidate_ranking": str(ranking_path) if ranking_path.exists() else None,
            "discovery_coverage": str(coverage_path) if coverage_path.exists() else None,
            "macro_snapshot": str(macro_snapshot_path) if macro_snapshot_path.exists() else None,
            "relative_strength": str(relative_strength_path) if relative_strength_path.exists() else None,
        },
        "portfolio": {
            "base_currency": portfolio_state.get("base_currency", "EUR"),
            "cash_eur": portfolio_state.get("cash_eur"),
            "total_portfolio_value_eur": portfolio_state.get("total_portfolio_value_eur"),
            "constraints": portfolio_state.get("constraints", {}),
        },
        "positions": positions,
        "pricing_audit": _read_json(pricing_audit_path) if pricing_audit_path else {},
        "macro_policy_pack": _read_json(macro_pack_path),
        "candidate_ranking": _read_json(ranking_path),
        "discovery_coverage": _read_json(coverage_path),
        "macro_snapshot": _read_json(macro_snapshot_path),
        "relative_strength": _read_json(relative_strength_path),
        "recommendation_scorecard": scorecard,
        "validation_flags": {
            "portfolio_state_present": bool(portfolio_state.get("positions")),
            "pricing_audit_present": pricing_audit_path is not None,
            "macro_policy_pack_present": bool(_read_json(macro_pack_path).get("regime")),
            "scorecard_present": bool(scorecard),
            "candidate_ranking_present": ranking_path.exists(),
            "benchmark_proxy_contract_visible": pricing_audit_path is not None,
        },
    }
    return runtime_state


def main() -> None:
    state = build_state()
    token = state.get("report_token") or datetime.utcnow().strftime("%y%m%d")
    out_path = RUNTIME_DIR / f"index_report_state_{token}.json"
    _write_json(out_path, state)
    print(
        "INDEX_RUNTIME_STATE_OK | "
        f"token={token} | output={out_path} | macro={state['source_files'].get('macro_policy_pack')} | pricing={state['source_files'].get('pricing_audit')}"
    )


if __name__ == "__main__":
    main()
