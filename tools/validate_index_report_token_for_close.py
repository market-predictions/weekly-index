from __future__ import annotations

import argparse
import re
from pathlib import Path

OUT = Path('output_indices')
REPORT_RE = re.compile(r'^weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$')


def token_from_close_date(close_date: str) -> str:
    yyyy, mm, dd = close_date.split('-')
    return f'{yyyy[2:]}{mm}{dd}'


def latest_report() -> tuple[str, int, Path]:
    hits = []
    for path in OUT.glob('weekly_indices_review_*.md'):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or '0'), path))
    if not hits:
        raise SystemExit('FAIL: no weekly_indices_review_*.md report found')
    hits.sort(key=lambda row: (row[0], row[1]))
    return hits[-1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--requested-close-date', required=True)
    args = parser.parse_args()

    expected = token_from_close_date(args.requested_close_date)
    token, version, path = latest_report()
    if token != expected:
        raise SystemExit(
            f'FAIL: latest canonical report token does not match requested close date: '
            f'latest_report={path.name} latest_token={token} expected_token={expected} '
            f'requested_close_date={args.requested_close_date}'
        )
    text = path.read_text(encoding='utf-8')
    expected_title = f'# Weekly Indices Review {args.requested_close_date}'
    if expected_title not in text.splitlines()[:5]:
        raise SystemExit(
            f'FAIL: report title date does not match requested close date: report={path.name} '
            f'expected_title={expected_title}'
        )
    print(f'INDEX_REPORT_TOKEN_OK | report={path.name} | token={token} | requested_close_date={args.requested_close_date}')


if __name__ == '__main__':
    main()
