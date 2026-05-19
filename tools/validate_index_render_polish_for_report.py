from __future__ import annotations

import argparse
import re
from pathlib import Path

BAD_TEXT_PATTERNS = [
    (re.compile(r'\b[Tt]he\s+the\b'), 'duplicate phrase: The the'),
]

BAD_HTML_PATTERNS = [
    (re.compile(r'<li\b', re.I), 'native list item tag; use inline markers to avoid PDF ghost bullets'),
    (re.compile(r'<ul\b', re.I), 'native unordered list tag; use inline markers to avoid PDF ghost bullets'),
    (re.compile(r'<ol\b', re.I), 'native ordered list tag; use inline markers to avoid PDF ghost numbering'),
    (re.compile(r'<li>\s*</li>', re.I), 'empty list item'),
    (re.compile(r'<li>\s*(?:-|\*|\+|\d+\.)\s*</li>', re.I), 'orphan list marker'),
    (re.compile(r'<p>\s*(?:-|\*|\+|\d+\.)\s*</p>', re.I), 'orphan marker paragraph'),
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
    plain = re.sub(r'<[^>]+>', ' ', html)
    plain = re.sub(r'\s+', ' ', plain)

    failures = []
    for pattern, label in BAD_TEXT_PATTERNS:
        if pattern.search(plain):
            failures.append(label)
    for pattern, label in BAD_HTML_PATTERNS:
        if pattern.search(html):
            failures.append(label)
    if failures:
        raise SystemExit('FAIL: render polish validation failed for ' + html_path.name + ': ' + ', '.join(failures))
    print(f'INDEX_RENDER_POLISH_OK | html={html_path.name}')


if __name__ == '__main__':
    main()
