import re
from pathlib import Path

OUT = Path('output_indices')
REPORT_RE = re.compile(r'^weekly_indices_review_(\d{6})(?:_(\d{2}))?_delivery\.html$')
REQUIRED_TICKERS = {
    'SPY', 'QQQ', 'IWM', 'EEM', 'EWJ', 'EWC', 'FXI', 'EWT', 'VLUE', 'EWY', 'QUAL', 'RSP', 'EWI', 'EWN', 'EWU', 'EWL', 'EWA', 'INDA', 'EWW', 'EWZ', 'EZA', 'EIDO', 'KSA', 'EWP', 'EWG', 'FEZ', 'EWH', 'EWQ', 'RWM', 'PSQ', 'EUM', 'USMV'
}


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
    path = latest_delivery_html()
    html = path.read_text(encoding='utf-8')
    missing = []
    for ticker in sorted(REQUIRED_TICKERS):
        visible = re.search(rf'(?<![A-Za-z0-9]){re.escape(ticker)}(?![A-Za-z0-9])', html)
        if not visible:
            continue
        expected = f'https://www.tradingview.com/chart/?symbol={ticker}'
        if expected not in html:
            missing.append(ticker)
    if missing:
        raise SystemExit('FAIL: visible tickers missing TradingView links in ' + path.name + ': ' + ', '.join(missing))
    print(f'INDEX_TICKER_LINKS_OK | html={path.name}')


if __name__ == '__main__':
    main()
