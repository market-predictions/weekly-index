from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED_TICKERS = {
    'SPY', 'QQQ', 'IWM', 'EEM', 'EWJ', 'EWC', 'FXI', 'EWT', 'VLUE', 'EWY', 'QUAL', 'RSP', 'EWI', 'EWN', 'EWU', 'EWL', 'EWA', 'INDA', 'EWW', 'EWZ', 'EZA', 'EIDO', 'KSA', 'EWP', 'EWG', 'FEZ', 'EWH', 'EWQ', 'RWM', 'PSQ', 'EUM', 'USMV'
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--report-path', required=True)
    args = parser.parse_args()

    report = Path(args.report_path)
    html_path = report.with_name(report.stem + '_delivery.html')
    if not html_path.exists():
        raise SystemExit(f'FAIL: delivery HTML missing for explicit report: {html_path}')
    html = html_path.read_text(encoding='utf-8')
    missing = []
    for ticker in sorted(REQUIRED_TICKERS):
        visible = re.search(rf'(?<![A-Za-z0-9]){re.escape(ticker)}(?![A-Za-z0-9])', html)
        if not visible:
            continue
        expected = f'https://www.tradingview.com/chart/?symbol={ticker}'
        if expected not in html:
            missing.append(ticker)
    if missing:
        raise SystemExit('FAIL: visible tickers missing TradingView links in ' + html_path.name + ': ' + ', '.join(missing))
    print(f'INDEX_TICKER_LINKS_OK | html={html_path.name}')


if __name__ == '__main__':
    main()
