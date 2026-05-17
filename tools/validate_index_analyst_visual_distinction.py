from pathlib import Path

OUT = Path('output_indices')
REQUIRED = [
    'analyst-hero',
    '#0F5B5C',
    'PART II',
    'Research depth, scenario framing and implementation detail',
    'page-break-before: always',
    'break-before: page',
]


def latest_delivery_html() -> Path:
    hits = sorted(OUT.glob('weekly_indices_review_*_delivery.html'))
    hits = [p for p in hits if '_clean' not in p.name]
    if not hits:
        raise SystemExit('FAIL: no delivery HTML found')
    return hits[-1]


def main() -> None:
    path = latest_delivery_html()
    html = path.read_text(encoding='utf-8')
    missing = [item for item in REQUIRED if item not in html]
    if missing:
        raise SystemExit('FAIL: Analyst visual distinction missing from ' + path.name + ': ' + ', '.join(missing))
    print(f'INDEX_ANALYST_VISUAL_DISTINCTION_OK | html={path.name}')


if __name__ == '__main__':
    main()
