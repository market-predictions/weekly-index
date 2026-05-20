from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import quote

# Keep this aligned with the ticker-link validator. The script adds
# deterministic TradingView markdown links to known tradable proxies before
# HTML/PDF rendering. It intentionally covers tables, headings, bullets and
# paragraph text because visible proxy tickers can appear in best-alternative
# explanations as well as tables.
KNOWN_TICKERS = {
    'SPY', 'QQQ', 'IWM', 'EEM', 'EWJ', 'EWC', 'FXI', 'EWT', 'VLUE', 'EWY',
    'QUAL', 'RSP', 'EWI', 'EWN', 'EWU', 'EWL', 'EWA', 'INDA', 'EWW', 'EWZ',
    'EZA', 'EIDO', 'KSA', 'EWP', 'EWG', 'FEZ', 'EWH', 'EWQ', 'RWM', 'PSQ',
    'EUM', 'USMV', 'QQQM', 'VOO', 'VWO', 'VTWO', 'DXJ', 'IEUR', 'SH', 'EFZ',
}

LINK_RE = re.compile(r"\[([^\]]+)\]\(https://www\.tradingview\.com/chart/\?symbol=[^)]+\)")
CODE_FENCE_RE = re.compile(r"^\s*```")
RAW_URL_RE = re.compile(r"https?://\S+")


def tv_url(ticker: str) -> str:
    return f"https://www.tradingview.com/chart/?symbol={quote(ticker, safe='')}"


def link_ticker(ticker: str) -> str:
    return f"[{ticker}]({tv_url(ticker)})"


def linkify_line(line: str) -> str:
    # Preserve already-linked markdown anchors and raw URLs before scanning for
    # bare ticker words. This prevents nested links and URL corruption.
    placeholders: list[str] = []

    def hold(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"@@TVLINK{len(placeholders) - 1}@@"

    protected = LINK_RE.sub(hold, line)
    protected = RAW_URL_RE.sub(hold, protected)
    for ticker in sorted(KNOWN_TICKERS, key=len, reverse=True):
        protected = re.sub(
            rf"(?<![A-Za-z0-9_]){re.escape(ticker)}(?![A-Za-z0-9_])",
            link_ticker(ticker),
            protected,
        )
    for idx, original in enumerate(placeholders):
        protected = protected.replace(f"@@TVLINK{idx}@@", original)
    return protected


def should_linkify(line: str, in_code_block: bool) -> bool:
    stripped = line.strip()
    if in_code_block or not stripped:
        return False
    if stripped.startswith('# Weekly'):
        return False
    if stripped.startswith('>'):
        return False
    if set(stripped.replace('|', '').replace(':', '').replace('-', '').replace(' ', '')) == set():
        return False
    return True


def linkify_report(path: Path) -> None:
    lines = path.read_text(encoding='utf-8').splitlines()
    out: list[str] = []
    in_code_block = False
    for line in lines:
        if CODE_FENCE_RE.match(line):
            out.append(line)
            in_code_block = not in_code_block
            continue
        out.append(linkify_line(line) if should_linkify(line, in_code_block) else line)
    path.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8')
    print(f"INDEX_TICKER_LINKIFY_OK | report={path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--report-path', required=True)
    args = parser.parse_args()
    linkify_report(Path(args.report_path))


if __name__ == '__main__':
    main()
