import re
from pathlib import Path

OUT = Path('output_indices')
REPORT_RE = re.compile(r'^weekly_indices_review_(\d{6})(?:_(\d{2}))?_delivery\.html$')

BAD_TEXT_PATTERNS = [
    (re.compile(r'\b[Tt]he\s+the\b'), 'duplicate phrase: The the'),
]

BAD_HTML_PATTERNS = [
    (re.compile(r'<li>\s*</li>', re.I), 'empty list item'),
    (re.compile(r'<li>\s*(?:-|\*|\+|\d+\.)\s*</li>', re.I), 'orphan list marker'),
    (re.compile(r'<p>\s*(?:-|\*|\+|\d+\.)\s*</p>', re.I), 'orphan marker paragraph'),
]


def latest_delivery_html() -> Path:
    hits = []
    for path in OUT.glob('weekly_indices_review_*_delivery.html'):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or '0'), path))
    if not hits:
        raise SystemExit('FAIL: no canonical weekly_indices_review_*_delivery.html found')
    hits.sort(key=lambda row: (row[0], row[1]))
    return hits[-1][2]


def main() -> None:
    html_path = latest_delivery_html()
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
