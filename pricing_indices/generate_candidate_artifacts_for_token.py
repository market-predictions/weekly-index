from __future__ import annotations

import argparse
from pathlib import Path

from . import generate_candidate_artifacts as base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='output_indices')
    parser.add_argument('--state-path', default='output_indices/index_portfolio_state.json')
    parser.add_argument('--token', required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    state_path = Path(args.state_path)
    token = args.token
    latest_report = output_dir / f'weekly_indices_review_{token}.md'
    if not latest_report.exists():
        raise FileNotFoundError(f'Missing requested-token report file: {latest_report}')
    if not state_path.exists():
        raise FileNotFoundError(f'Missing state file: {state_path}')

    state = base._read_json(state_path)
    plan = base.plan_for_token(output_dir, token)
    evidence = base.evidence_for_token(output_dir, token)

    candidates = base.evidence_candidates(state, evidence) if evidence else base.fallback_candidates(state, plan)
    candidates = base.assign_publish_flags(candidates)
    coverage = base.build_coverage(candidates)

    ranking_payload = {
        'report_date_token': token,
        'report_file': latest_report.name,
        'requested_close_date': evidence.get('requested_close_date') if evidence else None,
        'evidence_file': f'index_candidate_evidence_{token}.json' if evidence else None,
        'regional_group_status': coverage,
        'scan_summary': {
            'coverage_universe_count': len(candidates),
            'regional_group_count': len(base.GROUPS),
            'eligible_proxy_count': sum(1 for c in candidates if (c.get('proxy_eligibility') or {}).get('fundable_if_priced')),
            'compact_board_limit': 5,
            'rule': 'Broad scan universe first; compact board second. Candidates require proxy eligibility, pricing, regime fit and relative-strength evidence before funding.',
        },
        'candidates': candidates,
    }
    coverage_payload = {
        'report_date_token': token,
        'report_file': latest_report.name,
        'requested_close_date': evidence.get('requested_close_date') if evidence else None,
        'evidence_file': f'index_candidate_evidence_{token}.json' if evidence else None,
        'scan_summary': ranking_payload['scan_summary'],
        'groups': coverage,
    }

    ranking_path = output_dir / f'index_candidate_ranking_{token}.json'
    coverage_path = output_dir / f'index_discovery_coverage_{token}.json'
    base._write_json(ranking_path, ranking_payload)
    base._write_json(coverage_path, coverage_payload)

    surfaced = sum(1 for row in coverage if row['status'] == 'surfaced')
    near_miss = sum(1 for row in coverage if row['status'] == 'near_miss')
    evidence_mode = 'candidate_evidence_artifact' if evidence else 'fallback_regional_base_scores'
    print(
        f'CANDIDATE_ARTIFACTS_OK | report={latest_report.name} | token={token} | ranking={ranking_path.name} | coverage={coverage_path.name} | '
        f'scan_universe={len(candidates)} | surfaced_groups={surfaced} | near_miss_groups={near_miss} | mode={evidence_mode}'
    )


if __name__ == '__main__':
    main()
