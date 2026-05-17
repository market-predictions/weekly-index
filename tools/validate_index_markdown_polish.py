import re
from pathlib import Path

OUT = Path('output_indices')
REPORT_RE = re.compile(r'^weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$')
BAD_PATTERNS = [
    (re.compile(r'\b[Tt]he\s+the\b'), 'duplicate phrase: The the'),
    (re.compile(r'^\s*(?:[-*+]|\d+\.)\s*$', re.M), 'empty or orphan list marker'),
]


def latest_report() -> Path:
    hits = []
    for path in OUT.glob('weekly_indices_review_*.md'):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or '0'), path))
    if not hits:
        raise SystemExit('FAIL: no canonical weekly index markdown report found')
    hits.sort(key=lambda row: (row[0], row[1]))
    return hits[-1][2]


def main() -> None:
    path = latest_report()
    text = path.read_text(encoding='utf-8')
    failures = []
    for pattern, label in BAD_PATTERNS:
        if pattern.search(text):
            failures.append(label)
    if failures:
        raise SystemExit('FAIL: markdown polish validation failed for ' + path.name + ': ' + ', '.join(failures))
    print(f'INDEX_MARKDOWN_POLISH_OK | report={path.name}')


if __name__ == '__main__':
    main()
