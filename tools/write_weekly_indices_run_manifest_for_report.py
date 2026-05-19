#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_RE = re.compile(r'^weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$')
PRICE_AUDIT_RE = re.compile(r'^index_price_audit_(\d{4}-\d{2}-\d{2})\.json$')


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _safe_read_json(path: Path | None) -> dict[str, Any] | None:
    try:
        if path and path.exists():
            return _read_json(path)
    except Exception:
        return None
    return None


def _latest_price_audit(pricing_dir: Path) -> Path | None:
    hits: list[tuple[str, Path]] = []
    for path in pricing_dir.glob('index_price_audit_*.json'):
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
        with path.open('r', newline='', encoding='utf-8') as fh:
            return len(list(csv.reader(fh))) > 1
    except Exception:
        return False


def _section_present(text: str, heading: str) -> bool:
    return heading.lower() in text.lower()


def _section_contains(text: str, start_heading: str, needle: str) -> bool:
    lower = text.lower()
    start = lower.find(start_heading.lower())
    if start == -1:
        return False
    next_section = lower.find('\n## ', start + 1)
    section = lower[start:] if next_section == -1 else lower[start:next_section]
    return needle.lower() in section


def _token_from_report(report_path: Path) -> str:
    match = REPORT_RE.match(report_path.name)
    if not match:
        raise SystemExit(f'FAIL: invalid weekly index report filename: {report_path.name}')
    return match.group(1)


def _manifest_path(manifest_dir: Path, report_token: str) -> Path:
    run_id = os.getenv('GITHUB_RUN_ID') or 'local'
    run_attempt = os.getenv('GITHUB_RUN_ATTEMPT') or '1'
    return manifest_dir / f'weekly_indices_run_{report_token}_{run_id}_{run_attempt}.json'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='output_indices')
    parser.add_argument('--report-path', required=True)
    parser.add_argument('--conclusion', default='unknown')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    report_path = Path(args.report_path)
    report_token = _token_from_report(report_path)
    report_text = report_path.read_text(encoding='utf-8') if report_path.exists() else ''

    pricing_dir = output_dir / 'pricing'
    latest_audit_path = _latest_price_audit(pricing_dir)
    audit = _safe_read_json(latest_audit_path)
    state = _safe_read_json(output_dir / 'index_portfolio_state.json')
    ranking_path = output_dir / f'index_candidate_ranking_{report_token}.json'
    coverage_path = output_dir / f'index_discovery_coverage_{report_token}.json'
    ranking = _safe_read_json(ranking_path)
    coverage = _safe_read_json(coverage_path)

    ranking_candidates = (ranking or {}).get('candidates') or []
    published_candidates = [row for row in ranking_candidates if row.get('publish')]
    coverage_groups = (coverage or {}).get('groups') or []
    fx_basis = (audit or {}).get('fx_basis') or {}
    pricing_decision = (audit or {}).get('decision')

    manifest = {
        'schema_version': 1,
        'created_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'workflow': {
            'name': os.getenv('GITHUB_WORKFLOW'),
            'run_id': os.getenv('GITHUB_RUN_ID'),
            'run_attempt': os.getenv('GITHUB_RUN_ATTEMPT'),
            'job': os.getenv('GITHUB_JOB'),
            'actor': os.getenv('GITHUB_ACTOR'),
            'sha': os.getenv('GITHUB_SHA'),
            'ref': os.getenv('GITHUB_REF'),
            'conclusion': args.conclusion,
        },
        'report': {
            'file': str(report_path),
            'token': report_token,
            'composed_report_committed_expected': True,
            'scaffold_markers_present': [m for m in ['Pending workflow composition', 'Placeholder section for live workflow replacement', 'pending live pricing pass'] if m in report_text],
            'required_headings_present': {
                'executive_summary': _section_present(report_text, '## 1. Executive Summary'),
                'opportunity_board': _section_present(report_text, '## 4. Index Opportunity Board'),
                'equity_curve': _section_present(report_text, '## 7. Equity Curve and Portfolio Development'),
                'best_new_index_opportunities': _section_present(report_text, '## 11. Best New Index Opportunities'),
                'holdings_and_cash': _section_present(report_text, '## 15. Current Portfolio Holdings and Cash'),
                'continuity': _section_present(report_text, '## 16. Continuity Input for Next Run'),
            },
        },
        'pricing': {
            'audit_file': str(latest_audit_path) if latest_audit_path else None,
            'ok': pricing_decision == 'update_covered_holdings_carry_unresolved',
            'decision': pricing_decision,
            'requested_close_date': (audit or {}).get('requested_close_date'),
            'fx_date': fx_basis.get('date'),
            'fx_usd_per_eur': fx_basis.get('usd_per_eur'),
            'fresh_holdings_count': (audit or {}).get('fresh_holdings_count'),
            'holdings_count': (audit or {}).get('holdings_count'),
            'fresh_count_pct': (audit or {}).get('fresh_count_pct', (audit or {}).get('coverage_count_pct')),
            'fresh_invested_weight_coverage_pct': (audit or {}).get('fresh_invested_weight_coverage_pct'),
            'priced_invested_weight_coverage_pct': (audit or {}).get('priced_invested_weight_coverage_pct', (audit or {}).get('invested_weight_coverage_pct')),
            'unresolved_tickers': (audit or {}).get('unresolved_tickers', []),
        },
        'state': {
            'state_file': str(output_dir / 'index_portfolio_state.json'),
            'exists': bool(state),
            'requested_close_date': ((state or {}).get('pricing_basis') or {}).get('requested_close_date'),
            'fx_date': ((state or {}).get('pricing_basis') or {}).get('fx_date'),
            'total_portfolio_value_eur': (state or {}).get('total_portfolio_value_eur'),
            'cash_eur': (state or {}).get('cash_eur'),
            'positions_count': len((state or {}).get('positions') or []),
        },
        'breadth_and_opportunities': {
            'candidate_ranking_file': str(ranking_path),
            'discovery_coverage_file': str(coverage_path),
            'candidate_ranking_exists': bool(ranking),
            'discovery_coverage_exists': bool(coverage),
            'candidate_count': len(ranking_candidates),
            'published_candidate_count': len(published_candidates),
            'coverage_group_count': len(coverage_groups),
            'full_universe_breadth_ok': len(coverage_groups) >= 8,
            'long_opportunities_ok': len(ranking_candidates) > len(published_candidates),
            'short_opportunities_radar_ok': _section_contains(report_text, '## 11.', '### Long-side Opportunities') and _section_contains(report_text, '## 11.', '### Best Defensive / Inverse Opportunities') and any(t in report_text for t in ['RWM', 'PSQ', 'SH', 'EUM', 'EFZ']),
        },
        'scorecard': {
            'file': str(output_dir / 'index_recommendation_scorecard.csv'),
            'exists': (output_dir / 'index_recommendation_scorecard.csv').exists(),
            'has_rows': _csv_has_rows(output_dir / 'index_recommendation_scorecard.csv'),
        },
        'render_and_delivery': {
            'render_validation': 'unknown_without_workflow_step_failure_context',
            'email_delivery': 'unknown_without_send_script_receipt',
            'delivery_receipt_required_for_success_claim': True,
        },
    }

    manifest_dir = output_dir / 'run_manifests'
    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = _manifest_path(manifest_dir, report_token)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'RUN_MANIFEST_WRITTEN | path={path}')


if __name__ == '__main__':
    main()
