import re
from pathlib import Path

OUT = Path('output_indices')
REPORT_RE = re.compile(r'^weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$')
SECTION_RE = re.compile(r'^##\s+(\d+)\.', flags=re.MULTILINE)
PERFORMANCE_HEADER = '### Tradable Proxy Performance'
CHART_MARKERS = [
    '`EQUITY_CURVE_CHART_PLACEHOLDER`',
    'EQUITY_CURVE_CHART_PLACEHOLDER',
    '![Equity curve]',
    'Equity Curve (EUR)',
]


def latest_report() -> Path:
    hits = []
    for path in OUT.glob('weekly_indices_review_*.md'):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or '0'), path))
    if not hits:
        raise SystemExit('FAIL: no canonical weekly_indices_review_*.md report found')
    hits.sort(key=lambda row: (row[0], row[1]))
    return hits[-1][2]


def section_bounds(text: str, section_number: int) -> tuple[int, int]:
    matches = list(SECTION_RE.finditer(text))
    for idx, match in enumerate(matches):
        if int(match.group(1)) == section_number:
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            return match.start(), end
    raise SystemExit(f'FAIL: section {section_number} not found')


def first_chart_index(section7: str) -> int:
    indexes = [section7.find(marker) for marker in CHART_MARKERS if section7.find(marker) != -1]
    if not indexes:
        raise SystemExit('FAIL: no equity chart marker found in Section 7')
    return min(indexes)


def main() -> None:
    report = latest_report()
    text = report.read_text(encoding='utf-8')

    sec7_start, sec7_end = section_bounds(text, 7)
    sec15_start, sec15_end = section_bounds(text, 15)
    section7 = text[sec7_start:sec7_end]
    section15 = text[sec15_start:sec15_end]

    if PERFORMANCE_HEADER not in text:
        raise SystemExit('FAIL: Tradable Proxy Performance table is missing from the report')
    if PERFORMANCE_HEADER not in section7:
        raise SystemExit('FAIL: Tradable Proxy Performance is not in Section 7 after the equity chart')
    if PERFORMANCE_HEADER in section15:
        raise SystemExit('FAIL: Tradable Proxy Performance still appears in Section 15')

    chart_idx = first_chart_index(section7)
    perf_idx = section7.find(PERFORMANCE_HEADER)
    if perf_idx <= chart_idx:
        raise SystemExit('FAIL: Tradable Proxy Performance must appear after the equity chart marker')

    print(f'INDEX_PERFORMANCE_TABLE_PLACEMENT_OK | report={report.name}')


if __name__ == '__main__':
    main()
