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

CLIENT_REPLACEMENTS = [
    ('U.S. mega-cap growth leadership', 'Amerikaanse mega-cap groeileiderschap'),
    ('Broad emerging-market equity', 'Brede opkomende-marktenblootstelling'),
    ('U.S. large-cap core beta', 'Amerikaanse large-cap kernbeta'),
    ('Japan developed equity', 'Japanse ontwikkelde-marktenblootstelling'),
    ('U.S. small-cap breadth', 'Amerikaanse small-cap marktbreedte'),
    ('South Korea semiconductor / export cycle', 'Zuid-Koreaanse halfgeleider- en exportcyclus'),
    ('Taiwan semiconductor supply-chain leadership', 'Taiwanese halfgeleiderketen-leiderschap'),
    ('U.S. value factor', 'Amerikaanse value-factor'),
    ('Canada resources / financials', 'Canadese grondstoffen en financials'),
    ('U.S. core leadership', 'Amerikaanse kernmarktleiding'),
    ('U.S. factor / style alternatives', 'Amerikaanse factor- en stijlalternatieven'),
    ('developed Asia-Pacific', 'Ontwikkelde Azië-Pacific'),
    ('North America ex-U.S.', 'Noord-Amerika buiten VS'),
    ('continental Europe', 'Continentaal Europa'),
    ('Latin America', 'Latijns-Amerika'),
    ('Middle East', 'Midden-Oosten'),
    ('EM broad', 'Brede opkomende markten'),
    ('Greater China', 'Groot-China'),
    ('UK', 'Verenigd Koninkrijk'),
    ('Switzerland', 'Zwitserland'),
    ('Africa', 'Afrika'),
    ('Watchlist', 'Volglijst'),
    ('Tactische watchlist', 'Tactische volglijst'),
    ('Drawdown-hedge', 'Beschermende hedge'),
    ('drawdown-hedge', 'beschermende hedge'),
    ('Challenger-score', 'Overtuigingsscore /5'),
    ('Proxy-geschiktheid', 'Proxykwaliteit'),
    ('Gepubliceerd', 'Actief geselecteerd'),
    ('Sterke kandidaat, nog niet gefinancierd', 'Interessant, maar nog onvoldoende overtuiging'),
    ('Lagere prioriteit deze run', 'Niet aantrekkelijk genoeg deze week'),
    ('live gevolgd', 'actief gevolgd'),
    ('blijven gefinancierd', 'blijven opgenomen in portefeuille'),
    ('is gefinancierd', 'is opgenomen in portefeuille'),
    ('Gefinancierd, maar onder herbeoordeling.', 'Opgenomen in portefeuille, maar onder herbeoordeling.'),
    ('gefinancierde exposure', 'opgenomen positie'),
    ('verdiende sleeve', 'verdiende positie'),
]


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
- **Kernboodschap:** houd QQQ als sterkste verdiende positie, houd SPY onder concentratiecontrole en dwing IWM en EEM door expliciete long-alternatief- en defensieve hedge-duels voordat nieuw kapitaal wordt toegewezen."""


def add_section4_omitted(text: str, ranking: dict[str, Any]) -> str:
    bounds = section_bounds(text, 4)
    if not bounds or 'sterkste weggelaten regionale uitdager' in text[bounds[0]:bounds[1]]:
        return text
    candidates = [c for c in ranking.get('candidates', []) if not c.get('publish')]
    if not candidates:
        return text
    best = sorted(candidates, key=lambda c: float(c.get('challenger_score') or c.get('score') or 0.0), reverse=True)[0]
    line = f"\nHet bord blijft bewust compact. De sterkste weggelaten regionale uitdager deze run is **{best.get('public_index_name')} ({best.get('primary_proxy')})**, die relevant blijft zonder een hoger gerangschikte opgenomen positie te verdringen.\n"
    start, end = bounds
    return text[:end].rstrip() + line + '\n' + text[end:].lstrip()


def strip_tv_markdown_links(text: str) -> str:
    return TV_MD_LINK_RE.sub(r'\1', text)


def preserve_required_terms(text: str) -> str:
    # Keep terminology aligned with control/NL_TERMINOLOGY.md. Earlier client
    # polishing replaced every occurrence of "sleeve" with "positie", which
    # accidentally changed required table headers such as Portefeuillesleeve.
    return text.replace('Portefeuillepositie', 'Portefeuillesleeve')


def apply_client_language(text: str) -> str:
    for src, dst in CLIENT_REPLACEMENTS:
        text = text.replace(src, dst)
    text = preserve_required_terms(text)
    text = text.replace('Status vermogenscurve: actief gevolgd', 'Status vermogenscurve: actief gevolgd')
    text = text.replace('Waarom relevant: sterke kandidaat, maar nog niet gefinancierd.', 'Waarom relevant: interessant, maar nog onvoldoende overtuiging.')
    text = text.replace('Waarom nog niet op het bord: meer prijs-, regime- of relatieve-sterktebevestiging nodig.', 'Waarom nog niet geselecteerd: meer prijs-, regime- of relatieve-sterktebevestiging nodig.')
    return text


def score_to_conviction(score: Any) -> str:
    try:
        value = float(score)
    except (TypeError, ValueError):
        return 'Onbekend'
    if value >= 2.60:
        return 'Hoog'
    if value >= 2.00:
        return 'Gemiddeld'
    if value >= 1.25:
        return 'Laag tot gemiddeld'
    return 'Laag'


def add_score_explanations(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, score = match.group(1), match.group(2)
        return f"{prefix}{score} /5 ({score_to_conviction(score)}) |"
    return re.sub(r'(\|\s*)(\d+\.\d{2})(\s*\|\s*(?:Actief geselecteerd|Interessant, maar nog onvoldoende overtuiging|Niet aantrekkelijk genoeg deze week))', lambda m: repl(m) + m.group(3), text)


def add_week_actions(text: str) -> str:
    old = """### Top 3 acties deze week
1. Houd QQQ als sterkste kernpositie zolang het leiderschap intact blijft.
2. Toets SPY op overlap met QQQ, zodat Amerikaanse exposure niet wordt verward met volledige diversificatie.
3. Dwing IWM en EEM door long-alternatief- en defensieve/inverse vergelijkingen voordat extra kapitaal wordt toegevoegd."""
    new = """### Concrete weekacties
1. Zet geen nieuw kapitaal in totdat een uitdager zowel prijs, regime als relatieve sterkte bevestigt.
2. Vergelijk IWM direct met EWJ als long-alternatief en RWM als defensieve hedge.
3. Vergelijk EEM direct met FXI en INDA als long-alternatieven en EUM als defensieve hedge.
4. Bereid hedgeactivatie voor als marktbreedte verder verslechtert."""
    return text.replace(old, new)


def add_universe_coverage(text: str, ranking: dict[str, Any]) -> str:
    if '### Scandekking' in text:
        return text
    groups = ' '.join(str(g.get('group', '')) for g in ranking.get('regional_group_status', []))
    candidates = ' '.join(str(c.get('public_index_name', '')) + ' ' + str(c.get('regional_group', '')) for c in ranking.get('candidates', []))
    haystack = f'{groups} {candidates}'
    coverage = [
        ('VS', ['U.S.', 'Amerikaanse']),
        ('Europa', ['Europe', 'Europa', 'continental', 'Continentaal']),
        ('Japan', ['Japan', 'Nikkei']),
        ('China / Hongkong', ['China', 'Hong Kong', 'Greater China', 'Groot-China']),
        ('India', ['India', 'Nifty']),
        ('Korea / Taiwan', ['Korea', 'Taiwan']),
        ('Latijns-Amerika', ['Latin America', 'Latijns-Amerika', 'Mexico', 'Brazil']),
        ('Midden-Oosten', ['Middle East', 'Midden-Oosten', 'Saudi']),
        ('ASEAN', ['ASEAN', 'Indonesia']),
        ('Afrika', ['Africa', 'Afrika', 'South Africa']),
    ]
    lines = ['### Scandekking', '| Regio | Gedekt |', '|---|---|']
    for label, needles in coverage:
        covered = any(n in haystack for n in needles)
        lines.append(f"| {label} | {'✓' if covered else '—'} |")
    block = '\n'.join(lines) + '\n\n'
    marker = '## 5. Belangrijkste risico’s / ontkrachters'
    return text.replace(marker, block + marker, 1)


def add_reunderwriting_context(text: str) -> str:
    if 'Kapitaalherbeoordeling:' in text:
        return text
    text = text.replace('- Zou vandaag instappen:', '- Kapitaalherbeoordeling: beoordeel of deze positie vandaag opnieuw kapitaal verdient.\n- Zou vandaag instappen:', 1)
    return text


def render_v2(state: dict[str, Any], ranking: dict[str, Any], output_dir: Path, token: str) -> str:
    base.section7_table = section7_table_fixed
    close_date = base.text((state.get('pricing_basis') or {}).get('requested_close_date'), base.token_to_date(token))
    fx_date = base.text((state.get('pricing_basis') or {}).get('fx_date'), close_date)
    text = base.render_native_nl(state, ranking, output_dir, token)
    text = replace_section(text, 1, section1_fixed(state, close_date, fx_date))
    text = add_section4_omitted(text, ranking)
    text = add_week_actions(text)
    text = apply_client_language(text)
    text = add_score_explanations(text)
    text = add_universe_coverage(text, ranking)
    text = add_reunderwriting_context(text)
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
