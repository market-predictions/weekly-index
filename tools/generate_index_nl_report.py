#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

REPORT_RE = re.compile(r"weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")
SECTION_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$", re.M)

SECTION_TITLES_NL = {
    1: "Samenvatting",
    2: "Portefeuille-acties in één oogopslag",
    3: "Wereldwijd regimedashboard",
    4: "Indexkansenbord",
    5: "Belangrijkste risico’s / ontkrachters",
    6: "Kernconclusie",
    7: "Vermogenscurve en portefeuilleontwikkeling",
    8: "Regionale en stijlallocatiekaart",
    9: "Tweede-orde-effectenkaart",
    10: "Beoordeling huidige posities",
    11: "Beste nieuwe indexkansen",
    12: "Portefeuillerotatieplan",
    13: "Definitieve actietabel",
    14: "Positiewijzigingen in deze run",
    15: "Huidige portefeuilleposities en cash",
    16: "Continuïteitsinvoer voor de volgende run",
    17: "Disclaimer",
}

WEEKDAYS_NL = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
MONTHS_NL = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]

PHRASE_REPLACEMENTS = [
    ("Weekly Indices Review", "Weekly Index Review"),
    ("Executive Summary", "Samenvatting"),
    ("Portfolio Action Snapshot", "Portefeuille-acties in één oogopslag"),
    ("Global Regime Dashboard", "Wereldwijd regimedashboard"),
    ("Index Opportunity Board", "Indexkansenbord"),
    ("Key Risks / Invalidators", "Belangrijkste risico’s / ontkrachters"),
    ("Bottom Line", "Kernconclusie"),
    ("Equity Curve and Portfolio Development", "Vermogenscurve en portefeuilleontwikkeling"),
    ("Regional / Style Allocation Map", "Regionale en stijlallocatiekaart"),
    ("Second-Order Effects Map", "Tweede-orde-effectenkaart"),
    ("Current Position Review", "Beoordeling huidige posities"),
    ("Best New Index Opportunities", "Beste nieuwe indexkansen"),
    ("Portfolio Rotation Plan", "Portefeuillerotatieplan"),
    ("Final Action Table", "Definitieve actietabel"),
    ("Position Changes Executed This Run", "Positiewijzigingen in deze run"),
    ("Current Portfolio Holdings and Cash", "Huidige portefeuilleposities en cash"),
    ("Continuity Input for Next Run", "Continuïteitsinvoer voor de volgende run"),
    ("Disclaimer", "Disclaimer"),
    ("Investor Report", "Beleggersrapport"),
    ("Analyst Report", "Analistenrapport"),
    ("PART II", "DEEL II"),
    ("Research depth, scenario framing and implementation detail", "Onderzoeksdiepte, scenario’s en implementatiedetail"),
    ("Current valuation basis", "Huidige waarderingsbasis"),
    ("Primary regime", "Primair regime"),
    ("Geopolitical regime", "Geopolitiek regime"),
    ("Geopolitical implication", "Geopolitieke implicatie"),
    ("What changed", "Wat veranderde"),
    ("Portfolio implication", "Portefeuille-implicatie"),
    ("Main takeaway", "Kernboodschap"),
    ("Recommendation", "Aanbeveling"),
    ("Tickers / notes", "Tickers / opmerkingen"),
    ("Best replacements to monitor", "Beste vervangingen om te monitoren"),
    ("Top 3 actions this week", "Top 3 acties deze week"),
    ("Top 3 risks this week", "Top 3 risico’s deze week"),
    ("Starting capital (EUR)", "Startkapitaal (EUR)"),
    ("Current portfolio value (EUR)", "Huidige portefeuillewaarde (EUR)"),
    ("Since inception return (%)", "Rendement sinds start (%)"),
    ("Equity-curve state", "Status vermogenscurve"),
    ("Pricing basis requested close date", "Prijsbasis gevraagde slotdatum"),
    ("FX reference date", "FX-referentiedatum"),
    ("Portfolio value (EUR)", "Portefeuillewaarde (EUR)"),
    ("Tradable Proxy Performance", "Performance van verhandelbare proxy’s"),
    ("Performance is calculated on the tradable ETF proxies used for portfolio valuation. Benchmark index prices remain the analysis reference; tradable proxy closes drive market value, P/L and contribution.",
     "Performance wordt berekend op de verhandelbare ETF-proxy’s die voor portefeuillewaardering worden gebruikt. Benchmarkindexprijzen blijven het analyseanker; slotkoersen van verhandelbare proxy’s bepalen marktwaarde, winst/verlies en bijdrage."),
    ("Portfolio sleeve", "Portefeuillesleeve"),
    ("Benchmark index", "Benchmarkindex"),
    ("Tradable proxy", "Verhandelbare proxy"),
    ("Weight %", "Gewicht %"),
    ("1w return", "1w rendement"),
    ("1m return", "1m rendement"),
    ("3m return", "3m rendement"),
    ("Since-entry", "Sinds instap"),
    ("P/L EUR", "W/V EUR"),
    ("Contribution %", "Bijdrage %"),
    ("Region / style bucket", "Regio / stijlbucket"),
    ("Current view", "Huidige visie"),
    ("Comment", "Toelichting"),
    ("Ticker", "Ticker"),
    ("Shares", "Aandelen"),
    ("Price (local)", "Prijs (lokaal)"),
    ("Currency", "Valuta"),
    ("Market value (local)", "Marktwaarde (lokaal)"),
    ("Market value (EUR)", "Marktwaarde (EUR)"),
    ("Status", "Status"),
    ("Decision", "Besluit"),
    ("Required trigger", "Vereiste trigger"),
    ("Add", "Toevoegen"),
    ("Hold but replaceable", "Houden, maar vervangbaar"),
    ("Hold under review", "Houden, onder herbeoordeling"),
    ("Hold", "Houden"),
    ("Reduce", "Verlagen"),
    ("Close", "Sluiten"),
    ("Monitor", "Monitoren"),
    ("Watchlist", "Watchlist"),
    ("under review", "onder herbeoordeling"),
    ("No position changes were executed", "Er zijn geen positiewijzigingen uitgevoerd"),
    ("No new funded additions this run", "Geen nieuwe gefinancierde toevoegingen deze run"),
    ("This report is for informational and educational purposes only; please see the disclaimer at the end.", "Dit rapport is uitsluitend bedoeld voor informatieve en educatieve doeleinden; zie de disclaimer aan het einde."),
    ("This report is provided for informational and educational purposes only.", "Dit rapport is uitsluitend bedoeld voor informatieve en educatieve doeleinden."),
]

HEADER_REPLACEMENTS = {
    "| Portfolio sleeve | Benchmark index | Tradable proxy | Weight % | 1w return | 1m return | 3m return | Since-entry | P/L EUR | Contribution % |":
    "| Portefeuillesleeve | Benchmarkindex | Verhandelbare proxy | Gewicht % | 1w rendement | 1m rendement | 3m rendement | Sinds instap | W/V EUR | Bijdrage % |",
    "| Ticker | Public index / exposure | Shares | Price (local) | Currency | Market value (local) | Market value (EUR) | Weight % |":
    "| Ticker | Publieke index / exposure | Aandelen | Prijs (lokaal) | Valuta | Marktwaarde (lokaal) | Marktwaarde (EUR) | Gewicht % |",
    "| Date | Portfolio value (EUR) | Comment |":
    "| Datum | Portefeuillewaarde (EUR) | Toelichting |",
}


def token_from_report(path: Path) -> str:
    match = REPORT_RE.match(path.name)
    if not match:
        raise SystemExit(f"FAIL: not an English Weekly Index report filename: {path.name}")
    return match.group(1)


def date_from_token(token: str) -> str:
    return f"20{token[0:2]}-{token[2:4]}-{token[4:6]}"


def dutch_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{WEEKDAYS_NL[dt.weekday()]} {dt.day} {MONTHS_NL[dt.month - 1]} {dt.year}"


def localize_title(text: str, token: str) -> str:
    date_str = date_from_token(token)
    nl_date = dutch_date(date_str)
    text = re.sub(r"^#\s+Weekly Indices Review(?:\s+\d{4}-\d{2}-\d{2})?\s*$", f"# Weekly Index Review {nl_date}", text, count=1, flags=re.M)
    if not text.startswith("# Weekly Index Review"):
        text = f"# Weekly Index Review {nl_date}\n\n" + text
    return text


def translate_sections(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        number = int(match.group(1))
        title = SECTION_TITLES_NL.get(number, match.group(2))
        return f"## {number}. {title}"
    return SECTION_RE.sub(repl, text)


def apply_phrase_replacements(text: str) -> str:
    for source, target in HEADER_REPLACEMENTS.items():
        text = text.replace(source, target)
    for source, target in sorted(PHRASE_REPLACEMENTS, key=lambda x: len(x[0]), reverse=True):
        text = text.replace(source, target)
    return text


def localize_dates(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return dutch_date(match.group(1))
    return re.sub(r"\b(20\d{2}-\d{2}-\d{2})\b", repl, text)


def add_nl_header(text: str) -> str:
    note = (
        "\n\n> Nederlandse conceptversie. Deze versie gebruikt dezelfde data, prijsbasis, "
        "portefeuillewaarde, posities en beslissingen als het Engelse rapport.\n"
    )
    parts = text.split("\n", 1)
    if len(parts) == 2 and parts[0].startswith("# "):
        return parts[0] + note + "\n" + parts[1]
    return note + "\n" + text


def generate_nl(en_path: Path, nl_path: Path) -> None:
    token = token_from_report(en_path)
    text = en_path.read_text(encoding="utf-8")
    text = localize_title(text, token)
    text = translate_sections(text)
    text = apply_phrase_replacements(text)
    text = localize_dates(text)
    text = add_nl_header(text)
    nl_path.parent.mkdir(parents=True, exist_ok=True)
    nl_path.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(f"INDEX_NL_MARKDOWN_OK | en={en_path.name} | nl={nl_path.name} | token={token}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--en-report", required=True)
    parser.add_argument("--nl-report", default=None)
    args = parser.parse_args()
    en_path = Path(args.en_report)
    token = token_from_report(en_path)
    nl_path = Path(args.nl_report) if args.nl_report else en_path.with_name(f"weekly_indices_review_nl_{token}.md")
    generate_nl(en_path, nl_path)


if __name__ == "__main__":
    main()
