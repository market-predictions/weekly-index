from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED = [
    'analyst-hero',
    '#0F5B5C',
    'PART II',
    'Research depth, scenario framing and implementation detail',
    'page-break-before: always',
    'break-before: page',
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--report-path', required=True)
    args = parser.parse_args()

    report = Path(args.report_path)
    html_path = report.with_name(report.stem + '_delivery.html')
    if not html_path.exists():
        raise SystemExit(f'FAIL: delivery HTML missing for explicit report: {html_path}')
    html = html_path.read_text(encoding='utf-8')
    missing = [item for item in REQUIRED if item not in html]
    if missing:
        raise SystemExit('FAIL: Analyst visual distinction missing from ' + html_path.name + ': ' + ', '.join(missing))
    print(f'INDEX_ANALYST_VISUAL_DISTINCTION_OK | html={html_path.name}')


if __name__ == '__main__':
    main()
