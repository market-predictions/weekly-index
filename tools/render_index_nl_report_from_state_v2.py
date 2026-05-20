#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import re
from pathlib import Path
from typing import Any

BASE_PATH = Path(__file__).with_name('render_index_nl_report_from_state.py')
spec = importlib.util.spec_from_file_location('index_nl_base_renderer', BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError('Unable to load base Dutch renderer')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

SECTION_RE = re.compile(r'(^##\s+(\d+)\.\s+.*?$)', re.M)
TV_MD_LINK_RE = re.compile(r'\[([A-Z][A-Z0-9.\-]{1,11})\]\(https://www\.tradingview\.com/chart/\?symbol=[^)]+\)')


def section_bounds(text: str, number: int) -> tuple[int, int] | None:
    matches = list(SECTION_RE.finditer(text))
    for idx, match in enumerate(matches):
        if int(match.group(2)) == number:
            return match.start(), matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
    return None


def replace_section(text: str, number: int, replacement: str) -> str:
    bounds = section_bounds(text, number)
    if not bounds:
        return text
    start, end = bounds
    return text[:start] + replacement.rstrip() + '\n\n' + text[end:].lstrip()


def valuation_rows(output_dir: Path) -> list[dict[str, str]]:
    path = output_dir / 'index_valuation_history.csv'
    if not path.exists():
        return []
    by_close: dict[str, dict[str, str]] = {}
    with path.open(newline='', encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            close_date = (row.get('requested_close_date') or row.get('date') or '').strip()
            nav = (row.get('total_portfolio_value_eur') or row.get('nav_eur') or '').strip()
            if close_date and nav:
                by_close[close_date] = {'date': close_date, 'nav': nav}
    return [by_close[k] for k in sorted(by_close)]


def section7_table_fixed(state: dict[str, Any], output_dir: Path) -> str:
    lines = ['| Datum | Portefeuillewaarde (EUR) | Toelichting |', '|---|---:|---|']
    seen = set()
    for row in valuation_rows(output_dir):
        date = row['date']
        seen.add(date)
        lines.append(f"| {base.dutch_date(date)} | {base.f2(row['nav'])} | Prijsbasis slotkoers {base.dutch_date(date)} |")
    close_date = base.text((state.get('pricing_basis') or {}).get('requested_close_date'))
    if close_date and close_date not in seen:
        lines.append(f"| {base.dutch_date(close_date)} | {base.f2(base.nav(state))} | Prijsbasis slotkoers {base.dutch_date(close_date)} |")
    return '\n'.join(lines)


def section1_fixed(state: dict[str, Any], close_date: str, fx_date: str) -> str:
    return f"""## 1. Samenvatting
- **Huidige waarderingsbasis:** portefeuillewaarde is EUR {base.nav(state):,.2f}, inclusief EUR {base.cash(state):,.2f} cash, herbouwd op basis van de slotkoers van {base.dutch_date(close_date)} en FX-referentiedatum {base.dutch_date(fx_date)}.
- **Primair regime:** Risk-on met smalle Amerikaanse mega-cap marktleiding (72% vertrouwen).
- **Geopolitiek regime:** Rente- en energiegevoelig geopolitiek risico.
- **Geopolitieke implicatie:** Behandel olie, rentes en defensie-/geopolitieke schokken als risicofilters voor small caps, EM en Europa.
- **Wat veranderde:** Nasdaq-leiderschap is sterker dan small-cap marktbreedte; de risicobereidheid blijft dus smal in plaats van breed.
- **Portefeuille-implicatie:** Behandel smalle Amerikaanse marktleiding niet als volledige bevestiging van wereldwijde marktbreedte.
- **Kernboodschap:** houd QQQ als sterkste verdiende sleeve, houd SPY onder concentratiecontrole en dwing IWM en EEM door expliciete long-alternatief- en defensieve hedge-duels voordat nieuw kapitaal wordt toegewezen."""


def add_section4_omitted(text: str, ranking: dict[str, Any]) -> str:
    bounds = section_bounds(text, 4)
    if not bounds or 'sterkste weggelaten regionale uitdager' in text[bounds[0]:bounds[1]]:
        return text
    candidates = [c for c in ranking.get('candidates', []) if not c.get('publish')]
    if not candidates:
        return text
    best = sorted(candidates, key=lambda c: float(c.get('challenger_score') or c.get('score') or 0.0), reverse=True)[0]
    line = f"\nHet bord blijft bewust compact. De sterkste weggelaten regionale uitdager deze run is **{best.get('public_index_name')} ({best.get('primary_proxy')})**, die relevant blijft zonder een hoger gerangschikte gefinancierde exposure te verdringen.\n"
    start, end = bounds
    return text[:end].rstrip() + line + '\n' + text[end:].lstrip()


def strip_tv_markdown_links(text: str) -> str:
    return TV_MD_LINK_RE.sub(r'\1', text)


def render_v2(state: dict[str, Any], ranking: dict[str, Any], output_dir: Path, token: str) -> str:
    base.section7_table = section7_table_fixed
    close_date = base.text((state.get('pricing_basis') or {}).get('requested_close_date'), base.token_to_date(token))
    fx_date = base.text((state.get('pricing_basis') or {}).get('fx_date'), close_date)
    text = base.render_native_nl(state, ranking, output_dir, token)
    text = replace_section(text, 1, section1_fixed(state, close_date, fx_date))
    text = add_section4_omitted(text, ranking)
    return strip_tv_markdown_links(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', required=True)
    parser.add_argument('--output-dir', default='output_indices')
    parser.add_argument('--state-path', default='output_indices/index_portfolio_state.json')
    parser.add_argument('--nl-report', default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    state = base.read_json(Path(args.state_path))
    ranking = base.load_ranking(output_dir, args.token)
    nl_path = Path(args.nl_report) if args.nl_report else output_dir / f'weekly_indices_review_nl_{args.token}.md'
    nl_path.write_text(render_v2(state, ranking, output_dir, args.token).rstrip() + '\n', encoding='utf-8')
    print(f'INDEX_NL_NATIVE_RENDER_V2_OK | report={nl_path.name} | token={args.token}')


if __name__ == '__main__':
    main()
