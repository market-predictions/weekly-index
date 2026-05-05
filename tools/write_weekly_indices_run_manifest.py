#!/usr/bin/env python3
"""Write a machine-readable run manifest for Weekly Indices workflow runs.

The manifest is intentionally repo-native so delivery verification does not depend
only on GitHub Actions UI/API visibility. It can be executed at the end of a
workflow with `if: always()` and will summarize whatever artifacts exist.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_RE = re.compile(r"^weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")
PRICE_AUDIT_RE = re.compile(r"^index_price_audit_(\d{4}-\d{2}-\d{2})\.json$")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_read_json(path: Path) -> dict[str, Any] | None:
    try:
        if path.exists():
            return _read_json(path)
    except Exception:  # noqa: BLE001 - manifest should not hide prior workflow failures
        return None
    return None


def _latest_report(output_dir: Path) -> Path | None:
    hits: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_indices_review_*.md"):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or "0"), path))
    if not hits:
        return None
    hits.sort(key=lambda row: (row[0], row[1]))
    return hits[-1][2]


def _token_from_report(report_path: Path | None) -> str | None:
    if not report_path:
        return None
    match = REPORT_RE.match(report_path.name)
    return match.group(1) if match else None


def _latest_price_audit(pricing_dir: Path) -> Path | None:
    hits: list[tuple[str, Path]] = []
    for path in pricing_dir.glob("index_price_audit_*.json"):
        match = PRICE_AUDIT_RE.match(path.name)
        if match:
            hits.append((match.group(1), path))
    if not hits:
        return None
    hits.sort(key=lambda row: row[0])
    return hits[-1][1]


def _csv_has_rows(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        with path.open("r", newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            rows = list(reader)
        return len(rows) > 1
    except Exception:  # noqa: BLE001
        return False


def _section_present(text: str, heading: str) -> bool:
    return heading.lower() in text.lower()


def _section_contains(text: str, start_heading: str, needle: str) -> bool:
    lower = text.lower()
    start = lower.find(start_heading.lower())
    if start == -1:
        return False
    next_section = lower.find("\n## ", start + 1)
    section = lower[start:] if next_section == -1 else lower[start:next_section]
    return needle.lower() in section


def _manifest_path(manifest_dir: Path, report_token: str | None) -> Path:
    run_id = os.getenv("GITHUB_RUN_ID") or "local"
    run_attempt = os.getenv("GITHUB_RUN_ATTEMPT") or "1"
    token = report_token or datetime.now(timezone.utc).strftime("%y%m%d")
    return manifest_dir / f"weekly_indices_run_{token}_{run_id}_{run_attempt}.json"


def build_manifest(output_dir: Path, conclusion: str) -> dict[str, Any]:
    report_path = _latest_report(output_dir)
    report_token = _token_from_report(report_path)
    pricing_dir = output_dir / "pricing"
    latest_audit_path = _latest_price_audit(pricing_dir)
    audit = _safe_read_json(latest_audit_path) if latest_audit_path else None
    state = _safe_read_json(output_dir / "index_portfolio_state.json")

    ranking_path = output_dir / f"index_candidate_ranking_{report_token}.json" if report_token else None
    coverage_path = output_dir / f"index_discovery_coverage_{report_token}.json" if report_token else None
    ranking = _safe_read_json(ranking_path) if ranking_path else None
    coverage = _safe_read_json(coverage_path) if coverage_path else None

    report_text = report_path.read_text(encoding="utf-8") if report_path and report_path.exists() else ""
    scaffold_markers = [
        "Pending workflow composition",
        "Placeholder section for live workflow replacement",
        "pending live pricing pass",
    ]

    pricing_decision = (audit or {}).get("decision")
    pricing_ok = pricing_decision == "update_covered_holdings_carry_unresolved"
    fx_basis = (audit or {}).get("fx_basis") or {}

    ranking_candidates = (ranking or {}).get("candidates") or []
    published_candidates = [row for row in ranking_candidates if row.get("publish")]
    coverage_groups = (coverage or {}).get("groups") or []

    section11_has_long = _section_contains(report_text, "## 11.", "### Long-side Opportunities")
    section11_has_inverse = _section_contains(report_text, "## 11.", "### Best Defensive / Inverse Opportunities")
    section11_has_short_tools = any(token in report_text for token in ["RWM", "PSQ", "SH", "EUM", "EFZ"])

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workflow": {
            "name": os.getenv("GITHUB_WORKFLOW"),
            "run_id": os.getenv("GITHUB_RUN_ID"),
            "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
            "job": os.getenv("GITHUB_JOB"),
            "actor": os.getenv("GITHUB_ACTOR"),
            "sha": os.getenv("GITHUB_SHA"),
            "ref": os.getenv("GITHUB_REF"),
            "conclusion": conclusion,
        },
        "report": {
            "file": str(report_path) if report_path else None,
            "token": report_token,
            "composed_report_committed_expected": True,
            "scaffold_markers_present": [marker for marker in scaffold_markers if marker in report_text],
            "required_headings_present": {
                "executive_summary": _section_present(report_text, "## 1. Executive Summary"),
                "opportunity_board": _section_present(report_text, "## 4. Index Opportunity Board"),
                "equity_curve": _section_present(report_text, "## 7. Equity Curve and Portfolio Development"),
                "best_new_index_opportunities": _section_present(report_text, "## 11. Best New Index Opportunities"),
                "holdings_and_cash": _section_present(report_text, "## 15. Current Portfolio Holdings and Cash"),
                "continuity": _section_present(report_text, "## 16. Continuity Input for Next Run"),
            },
        },
        "pricing": {
            "audit_file": str(latest_audit_path) if latest_audit_path else None,
            "ok": pricing_ok,
            "decision": pricing_decision,
            "requested_close_date": (audit or {}).get("requested_close_date"),
            "fx_date": fx_basis.get("date"),
            "fx_usd_per_eur": fx_basis.get("usd_per_eur"),
            "fresh_holdings_count": (audit or {}).get("fresh_holdings_count"),
            "holdings_count": (audit or {}).get("holdings_count"),
            "fresh_count_pct": (audit or {}).get("fresh_count_pct", (audit or {}).get("coverage_count_pct")),
            "fresh_invested_weight_coverage_pct": (audit or {}).get("fresh_invested_weight_coverage_pct"),
            "priced_invested_weight_coverage_pct": (audit or {}).get("priced_invested_weight_coverage_pct", (audit or {}).get("invested_weight_coverage_pct")),
            "unresolved_tickers": (audit or {}).get("unresolved_tickers", []),
        },
        "state": {
            "state_file": str(output_dir / "index_portfolio_state.json"),
            "exists": bool(state),
            "requested_close_date": ((state or {}).get("pricing_basis") or {}).get("requested_close_date"),
            "fx_date": ((state or {}).get("pricing_basis") or {}).get("fx_date"),
            "total_portfolio_value_eur": (state or {}).get("total_portfolio_value_eur"),
            "cash_eur": (state or {}).get("cash_eur"),
            "positions_count": len((state or {}).get("positions") or []),
        },
        "breadth_and_opportunities": {
            "candidate_ranking_file": str(ranking_path) if ranking_path else None,
            "discovery_coverage_file": str(coverage_path) if coverage_path else None,
            "candidate_ranking_exists": bool(ranking),
            "discovery_coverage_exists": bool(coverage),
            "candidate_count": len(ranking_candidates),
            "published_candidate_count": len(published_candidates),
            "coverage_group_count": len(coverage_groups),
            "full_universe_breadth_ok": len(coverage_groups) >= 8,
            "long_opportunities_ok": len(ranking_candidates) > len(published_candidates),
            "short_opportunities_radar_ok": section11_has_long and section11_has_inverse and section11_has_short_tools,
        },
        "scorecard": {
            "file": str(output_dir / "index_recommendation_scorecard.csv"),
            "exists": (output_dir / "index_recommendation_scorecard.csv").exists(),
            "has_rows": _csv_has_rows(output_dir / "index_recommendation_scorecard.csv"),
        },
        "render_and_delivery": {
            "render_validation": "unknown_without_workflow_step_failure_context",
            "email_delivery": "unknown_without_send_script_receipt",
            "delivery_receipt_required_for_success_claim": True,
        },
    }
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output_indices")
    parser.add_argument("--conclusion", default="unknown")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    manifest = build_manifest(output_dir, args.conclusion)
    manifest_dir = output_dir / "run_manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = _manifest_path(manifest_dir, manifest["report"].get("token"))
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"RUN_MANIFEST_WRITTEN | path={path}")


if __name__ == "__main__":
    main()
