from __future__ import annotations

import argparse
import re
from pathlib import Path

OUT = Path('output_indices')
REPORT_RE = re.compile(r'^weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$')


def token_from_close_date(close_date: str) -> str:
    yyyy, mm, dd = close_date.split('-')
    return f'{yyyy[2:]}{mm}{dd}'


def latest_report() -> Path:
    hits = []
    for path in OUT.glob('weekly_indices_review_*.md'):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or '0'), path))
    if not hits:
        raise SystemExit('FAIL: no existing weekly index report found to use as template')
    hits.sort(key=lambda row: (row[0], row[1]))
    return hits[-1][2]


def target_path(token: str) -> Path:
    return OUT / f'weekly_indices_review_{token}.md'


def set_report_date(text: str, requested_close_date: str) -> str:
    replacement = f'# Weekly Indices Review {requested_close_date}'
    updated = re.sub(
        r'^#\s+Weekly Indices Review(?:\s+\d{4}-\d{2}-\d{2})?\s*$',
        replacement,
        text,
        count=1,
        flags=re.M,
    )
    if updated == text and not text.startswith('# Weekly Indices Review'):
        updated = replacement + '\n\n' + text
    return updated.rstrip() + '\n'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--requested-close-date', required=True)
    args = parser.parse_args()

    token = token_from_close_date(args.requested_close_date)
    target = target_path(token)

    if target.exists():
        text = target.read_text(encoding='utf-8')
        target.write_text(set_report_date(text, args.requested_close_date), encoding='utf-8')
        print(f'INDEX_REPORT_PREPARED | report={target.name} | token={token} | already_exists=yes')
        return

    source = latest_report()
    text = source.read_text(encoding='utf-8')
    target.write_text(set_report_date(text, args.requested_close_date), encoding='utf-8')

    if not target.exists():
        raise SystemExit(f'FAIL: requested report token was not created: {target}')
    print(f'INDEX_REPORT_PREPARED | report={target.name} | token={token} | source={source.name} | created=yes')


if __name__ == '__main__':
    main()
