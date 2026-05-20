#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

WEEKDAYS_NL = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
MONTHS_NL = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]

ROLE_NL = {
    "core beta": "kernbeta",
    "growth engine": "groeimotor",
    "breadth diversifier": "marktbreedte-diversifier",
    "non-U.S. risk sleeve": "niet-Amerikaanse risicosleeve",
}

STATUS_NL = {
    "hold": "Houden",
    "add": "Toevoegen",
    "reduce": "Verlagen",
    "close": "Sluiten",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def f2(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return ""


def pct(value: Any, signed: bool = False) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n.v.t."
    sign = "+" if signed and number > 0 else ""
    return f"{sign}{number:.2f}%"


def text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw if raw else fallback


def ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def dutch_date(value: str) -> str:
    dt = datetime.strptime(value, "%Y-%m-%d")
    return f"{WEEKDAYS_NL[dt.weekday()]} {dt.day} {MONTHS_NL[dt.month - 1]} {dt.year}"


def token_to_date(token: str) -> str:
    return f"20{token[:2]}-{token[2:4]}-{token[4:6]}"


def positions(state: dict[str, Any]) -> list[dict[str, Any]]:
    return list(state.get("positions") or [])


def nav(state: dict[str, Any]) -> float:
    return float(state.get("total_portfolio_value_eur") or 0.0)


def cash(state: dict[str, Any]) -> float:
    return float(state.get("cash_eur") or 0.0)


def invested(state: dict[str, Any]) -> float:
    return round(sum(float(p.get("market_value_eur") or 0.0) for p in positions(state)), 2)


def role_nl(value: Any) -> str:
    raw = text(value)
    return ROLE_NL.get(raw, raw or "positie")


def status_nl(value: Any) -> str:
    raw = text(value, "hold").lower()
    return STATUS_NL.get(raw, "Houden")


def thesis_nl(position: dict[str, Any]) -> str:
    proxy = ticker(position.get("primary_proxy"))
    return {
        "SPY": "Amerikaanse large-cap kernblootstelling in een gemengd regime.",
        "QQQ": "Technologieleiderschap blijft de sterkste groeimotor.",
        "IWM": "Small-cap blootstelling blijft nuttig als marktbreedte-diversifier, maar staat onder herbeoordeling.",
        "EEM": "Gemeten niet-Amerikaanse risicosleeve, maar gevoelig voor USD- en oliedruk.",
    }.get(proxy, text(position.get("original_thesis"), "Portefeuilleblootstelling."))


def next_action_nl(position: dict[str, Any]) -> str:
    proxy = ticker(position.get("primary_proxy"))
    return {
        "SPY": "Toets overlap met QQQ voordat extra kapitaal wordt toegewezen.",
        "QQQ": "Houd als kernpositie zolang technologieleiderschap intact blijft.",
        "IWM": "Dwing een direct alternatief-duel af tegenover EWJ en RWM.",
        "EEM": "Dwing een direct alternatief-duel af tegenover FXI, INDA en EUM.",
    }.get(proxy, "Aanhouden en opnieuw toetsen in de volgende run.")


def candidate_status_nl(status: str) -> str:
    return {
        "surfaced": "Gepubliceerd",
        "near_miss": "Sterke kandidaat, nog niet gefinancierd",
        "ruled_out": "Lagere prioriteit deze run",
    }.get(status, status or "Volglijst")


def proxy_eligibility_nl(note: str) -> str:
    if "Funded" in note:
        return "Gefinancierd of direct financierbaar als portefeuilleregels dit toelaten."
    if "Liquid country ETF" in note:
        return "Liquide landen-ETF; geschikt voor ranking mits prijsdata en macrofit kloppen."
    if "Liquid U.S.-listed ETF" in note:
        return "Liquide Amerikaanse ETF; geschikt voor ranking mits prijsdata en historie kloppen."
    return "Geschikte proxy, onder voorbehoud van prijsdata en portefeuilleregels."


def load_ranking(output_dir: Path, token: str) -> dict[str, Any]:
    path = output_dir / f"index_candidate_ranking_{token}.json"
    return read_json(path) if path.exists() else {}


def published_candidates(ranking: dict[str, Any]) -> list[dict[str, Any]]:
    return [c for c in ranking.get("candidates", []) if c.get("publish")][:5]


def challenger_candidates(ranking: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [c for c in ranking.get("candidates", []) if not c.get("publish")]
    return sorted(rows, key=lambda c: float(c.get("challenger_score") or c.get("score") or 0.0), reverse=True)[:6]


def regional_groups(ranking: dict[str, Any]) -> list[dict[str, Any]]:
    return list(ranking.get("regional_group_status") or [])[:15]


def valuation_history(output_dir: Path) -> list[dict[str, str]]:
    path = output_dir / "index_valuation_history.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def section7_table(state: dict[str, Any], output_dir: Path) -> str:
    lines = ["| Datum | Portefeuillewaarde (EUR) | Toelichting |", "|---|---:|---|"]
    seen = set()
    for row in valuation_history(output_dir):
        date = text(row.get("date"))
        value = text(row.get("nav_eur"))
        if not date or not value:
            continue
        seen.add(date)
        comment = "Prijsbasis slotkoers " + dutch_date(date)
        lines.append(f"| {dutch_date(date)} | {f2(value)} | {comment} |")
    close_date = text((state.get("pricing_basis") or {}).get("requested_close_date"))
    if close_date and close_date not in seen:
        lines.append(f"| {dutch_date(close_date)} | {f2(nav(state))} | Prijsbasis slotkoers {dutch_date(close_date)} |")
    return "\n".join(lines)


def performance_table(state: dict[str, Any]) -> str:
    lines = [
        "| Portefeuillesleeve | Benchmarkindex | Verhandelbare proxy | Gewicht % | 1w rendement | 1m rendement | 3m rendement | Sinds instap | W/V EUR | Bijdrage % |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in positions(state):
        perf = p.get("performance") or {}
        lines.append(
            f"| {p.get('display_name')} | {p.get('benchmark_name')} | {p.get('primary_proxy')} | "
            f"{f2(p.get('weight_pct'))} | {pct(perf.get('one_week_return_pct'), signed=True)} | {pct(perf.get('one_month_return_pct'), signed=True)} | "
            f"{pct(perf.get('three_month_return_pct'), signed=True)} | {pct(perf.get('since_entry_return_pct'), signed=True)} | "
            f"{f2(perf.get('pnl_eur'))} | {pct(perf.get('contribution_pct'), signed=True)} |"
        )
    return "\n".join(lines)


def holdings_table(state: dict[str, Any]) -> str:
    lines = [
        "| Ticker | Publieke index / exposure | Aandelen | Prijs (lokaal) | Valuta | Marktwaarde (lokaal) | Marktwaarde (EUR) | Gewicht % |",
        "|---|---|---:|---:|---|---:|---:|---:|",
    ]
    for p in positions(state):
        lines.append(
            f"| {p.get('primary_proxy')} | {p.get('display_name')} | {f2(p.get('shares'))} | {f2(p.get('latest_proxy_close'))} | {p.get('proxy_currency')} | "
            f"{f2(p.get('market_value_local'))} | {f2(p.get('market_value_eur'))} | {f2(p.get('weight_pct'))} |"
        )
    cash_pct = cash(state) / (nav(state) or 1.0) * 100.0
    lines.append(f"| CASH | Cash | - | 1.00 | EUR | {f2(cash(state))} | {f2(cash(state))} | {f2(cash_pct)} |")
    return "\n".join(lines)


def opportunity_board(ranking: dict[str, Any]) -> str:
    lines = [
        "| Portefeuillesleeve | Benchmarkindex | Verhandelbare proxy | Regio / stijlbucket | Score | Status | Reden voor opname |",
        "|---|---|---|---|---:|---|---|",
    ]
    for c in published_candidates(ranking):
        reason = "Past bij het huidige regime en behoudt voldoende prijs- en relatieve-sterktebewijs."
        if c.get("primary_proxy") == "QQQ":
            reason = "Groeileiderschap blijft de kernmotor in de huidige kansenlijst."
        elif c.get("primary_proxy") == "SPY":
            reason = "Amerikaanse large-cap kernblootstelling blijft het zuiverste anker."
        elif c.get("primary_proxy") == "EWJ":
            reason = "Japan verbetert de ontwikkelde ex-VS-breedte zonder lage overtuiging te forceren."
        lines.append(f"| {c.get('portfolio_sleeve')} | {c.get('benchmark_name')} | {c.get('primary_proxy')} | {c.get('regional_group')} | {f2(c.get('score'))} | Gepubliceerd | {reason} |")
    return "\n".join(lines)


def regional_map() -> str:
    return "\n".join([
        "| Regio / stijlbucket | Huidige visie | Toelichting |",
        "|---|---|---|",
        "| Amerikaanse mega-cap / kwaliteitsgroei | Overwogen | QQQ blijft de sterkste sleeve. |",
        "| Amerikaanse brede large cap | Neutraal-positief | SPY werkt nog, maar overlap met QQQ moet worden getoetst. |",
        "| Amerikaanse small cap | Onder actieve herbeoordeling | IWM is gefinancierd, maar geen passieve hold meer. |",
        "| Continentaal Europa | Onderwogen | Olie- en geopolitieke gevoeligheid blijven een rem. |",
        "| Verenigd Koninkrijk | Lagere prioriteit | Nog niet sterk genoeg tegenover Japan of Canada. |",
        "| Zwitserland | Watchlist | Defensieve kwaliteit, maar nog niet topgerangschikt. |",
        "| Noord-Amerika ex-VS | Verbeterend | Canada blijft een echte uitdager. |",
        "| Japan | Positief | Sterkste ontwikkelde ex-VS-lane. |",
        "| Greater China | Tactische watchlist | FXI blijft een echte marktbreedtekandidaat. |",
        "| EM breed | Neutraal-positief maar onder herbeoordeling | EEM moet selectievere alternatieven verslaan. |",
    ])


def current_position_review(state: dict[str, Any]) -> str:
    blocks = []
    for p in positions(state):
        proxy = p.get("primary_proxy")
        initiate = "Ja" if proxy in {"SPY", "QQQ"} else "Kleiner / onopgelost"
        current_weight = "Ja" if proxy in {"SPY", "QQQ"} else "Nee"
        thesis_score = {"SPY": "4.1", "QQQ": "4.4", "IWM": "3.2", "EEM": "3.3"}.get(proxy, "3.0")
        implementation_score = {"SPY": "3.9", "QQQ": "4.3", "IWM": "2.9", "EEM": "2.9"}.get(proxy, "3.0")
        alt = {"SPY": "VOO / QUAL / gedeeltelijke rotatie naar EWJ", "QQQ": "QQQM", "IWM": "EWJ long-side, RWM defensief", "EEM": "FXI / INDA long-side, EUM defensief"}.get(proxy, text(p.get("alternative_proxy")))
        blocks.append(
            f"### {p.get('display_name')} / {proxy}\n"
            f"- Zou vandaag instappen: {initiate}.\n"
            f"- Zou instappen op huidig gewicht: {current_weight}.\n"
            f"- Thesescore: {thesis_score} / 5.\n"
            f"- Implementatiescore: {implementation_score} / 5.\n"
            f"- Beste alternatief: {alt}.\n"
            f"- Vereiste volgende actie: {next_action_nl(p)}\n"
        )
    return "\n".join(blocks)


def best_new_opportunities(ranking: dict[str, Any]) -> str:
    lines = ["### Long-kansen", ""]
    for idx, c in enumerate(challenger_candidates(ranking)[:4], 1):
        lines.extend([
            f"#### {idx}. {c.get('public_index_name')} ({c.get('primary_proxy')})",
            f"- Portefeuillesleeve: {c.get('portfolio_sleeve')}",
            f"- Regio / stijlbucket: {c.get('regional_group')}",
            f"- Challenger-score: {f2(c.get('challenger_score') or c.get('score'))}",
            f"- Proxy-geschiktheid: {proxy_eligibility_nl(((c.get('proxy_eligibility') or {}).get('note') or ''))}",
            "- Waarom relevant: sterke kandidaat, maar nog niet gefinancierd.",
            "- Waarom nog niet op het bord: meer prijs-, regime- of relatieve-sterktebevestiging nodig.",
            "",
        ])
    lines.extend([
        "### Beste defensieve / inverse kansen",
        "Deze instrumenten zijn uitsluitend defensieve instrumenten. Ze maken geen deel uit van de basisscenario-longallocatie.",
        "",
        "| Kandidaat | Onderliggende waarde | Status | Short-these | Trigger | Ontkrachting | Maximale rol |",
        "|---|---|---|---|---|---|---|",
        "| RWM | IWM / Russell 2000 | Watchlist | Small caps blijven kwetsbaar als marktbreedte zwak blijft en reële rentes restrictief zijn. | IWM blijft achter bij SPY terwijl krediet en breedte niet verbeteren. | Breed herstel door versoepeling en betere small-cap relatieve sterkte. | Alleen defensieve hedge. |",
        "| EUM | EEM / Emerging Markets | Watchlist | EM blijft kwetsbaar bij USD-druk en zwakker Chinavertrouwen. | UUP versterkt terwijl EEM relatieve steun breekt. | USD verzwakt en China/EM-breedte bevestigt opwaarts potentieel. | Alleen defensieve hedge. |",
        "| PSQ | QQQ / Nasdaq 100 | Monitor | Nasdaq-hedge alleen relevant als mega-cap leiderschap breekt. | QQQ verliest relatieve sterkte tegenover SPY. | QQQ-leiderschap blijft intact. | Drawdown-hedge. |",
    ])
    return "\n".join(lines)


def breadth_checkpoint(ranking: dict[str, Any]) -> str:
    lines = [
        "### Marktbreedtecheck per regionale bucket",
        "| Regio / stijlbucket | Sterkste kandidaat | Proxy | Aantal kandidaten | Geschikte proxy’s | Challenger-score | Huidige status |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for g in regional_groups(ranking):
        c = g.get("strongest_candidate") or {}
        lines.append(f"| {g.get('group')} | {c.get('public_index_name')} | {c.get('primary_proxy')} | {g.get('candidate_count')} | {g.get('eligible_proxy_count')} | {f2(c.get('challenger_score') or c.get('score'))} | {candidate_status_nl(g.get('status'))} |")
    return "\n".join(lines)


def final_action_table(state: dict[str, Any]) -> str:
    lines = ["| Ticker | Exposure | Gewicht % | Advies | Rol | Korte toelichting |", "|---|---|---:|---|---|---|"]
    for p in positions(state):
        proxy = p.get("primary_proxy")
        advice = "Houden" if proxy in {"SPY", "QQQ"} else "Houden, onder herbeoordeling"
        lines.append(f"| {proxy} | {p.get('display_name')} | {f2(p.get('weight_pct'))} | {advice} | {role_nl(p.get('role'))} | {thesis_nl(p)} |")
    return "\n".join(lines)


def continuity_table(state: dict[str, Any]) -> str:
    lines = ["| Ticker | Index / exposure | Richting | Gewicht % | Gem. instap | Huidige prijs | W/V % | Thesis | Rol |", "|---|---|---|---:|---:|---:|---:|---|---|"]
    for p in positions(state):
        perf = p.get("performance") or {}
        lines.append(f"| {p.get('primary_proxy')} | {p.get('display_name')} | Long | {f2(p.get('weight_pct'))} | {f2(p.get('avg_entry_proxy'))} | {f2(p.get('latest_proxy_close'))} | {pct(perf.get('since_entry_return_pct'), signed=True)} | {thesis_nl(p)} | {role_nl(p.get('role'))} |")
    return "\n".join(lines)


def render_native_nl(state: dict[str, Any], ranking: dict[str, Any], output_dir: Path, token: str) -> str:
    close_date = text((state.get("pricing_basis") or {}).get("requested_close_date"), token_to_date(token))
    fx_date = text((state.get("pricing_basis") or {}).get("fx_date"), close_date)
    current_nav = nav(state)
    current_cash = cash(state)
    return f"""# Weekly Index Review {dutch_date(close_date)}

> Nederlandse conceptversie. Deze versie gebruikt dezelfde data, prijsbasis, portefeuillewaarde, posities en beslissingen als het Engelse rapport.

> *Dit rapport is uitsluitend bedoeld voor informatieve en educatieve doeleinden; zie de disclaimer aan het einde.*

## 1. Samenvatting
- **Huidige waarderingsbasis:** portefeuillewaarde is EUR {current_nav:,.2f}, inclusief EUR {current_cash:,.2f} cash, herbouwd op basis van de slotkoers van {dutch_date(close_date)} en FX-referentiedatum {dutch_date(fx_date)}.
- **Primair regime:** risk-on met smalle Amerikaanse mega-cap marktleiding.
- **Geopolitiek regime:** verhoogd USD- / beleidsfrictierisico.
- **Portefeuille-implicatie:** behandel smalle Amerikaanse marktleiding niet als volledige bevestiging van wereldwijde marktbreedte.
- **Kernboodschap:** houd QQQ als sterkste verdiende sleeve, houd SPY onder concentratiecontrole en dwing IWM en EEM door expliciete alternatief- en hedge-duels voordat nieuw kapitaal wordt toegewezen.

## 2. Portefeuille-acties in één oogopslag
| Aanbeveling | Tickers / opmerkingen |
|---|---|
| Toevoegen | Geen toevoeging deze run. Cash blijft beschikbaar, maar nog geen uitdager haalt de volledige drempel voor prijs, regime en relatieve sterkte. |
| Houden | S&P 500 via SPY; Nasdaq 100 via QQQ |
| Houden, maar vervangbaar | Russell 2000 via IWM; Emerging Markets via EEM |
| Verlagen | Geen verlaging totdat het directe alternatief-duel een schonere vervanging of hedge-trigger oplevert. |
| Sluiten | Geen actie deze run. |

### Beste vervangingen om te monitoren
- Japan large cap via EWJ
- Canada breed via EWC
- Greater China large cap via FXI

### Top 3 acties deze week
1. Houd QQQ als sterkste kernpositie zolang het leiderschap intact blijft.
2. Toets SPY op overlap met QQQ, zodat Amerikaanse exposure niet wordt verward met volledige diversificatie.
3. Dwing IWM en EEM door long-alternatief- en defensieve/inverse vergelijkingen voordat extra kapitaal wordt toegevoegd.

### Top 3 risico’s deze week
1. Hogere olieprijzen of hardnekkige inflatie vertragen ruimer beleid en houden druk op zwakke marktbreedte.
2. SPY en QQQ blijven een concentratiecluster, geen gediversifieerde wereldwijde allocatie.
3. IWM en EEM blijven onder herbeoordeling totdat marktbreedte, USD-beeld en relatieve sterkte verbeteren.

## 3. Wereldwijd regimedashboard
| Lens | Huidige lezing | Portefeuille-implicatie |
|---|---|---|
| Amerikaanse groei / winst | Nog altijd veerkrachtig; AI en halfgeleiders blijven leiden | Ondersteunt QQQ en houdt SPY valide |
| Inflatie | Hogere olieprijzen brengen inflatiezorgen terug | Houdt druk op cyclische waarden met lage marges |
| Beleidspad | Verwachtingen voor Fed-renteverlagingen zijn naar achteren geschoven | Minder gunstig voor small caps en rentegevoelige beta |
| Europa | Vlak tot zwakker koersbeeld door olie- en geopolitieke druk | Europa blijft voorlopig onder de selectielijn |
| Japan | Betere relatieve setup dan breed Europa | EWJ blijft een geloofwaardige toevoegingskandidaat |
| Canada | Grondstoffensteun verbetert de casus | EWC blijft een echte uitdager, geen opvulling |
| EM | Nog belegbaar, maar gevoeliger voor dollar- en oliedruk | EEM moet streng worden getoetst tegenover alternatieven |

## 4. Indexkansenbord
De scan omvat **{(ranking.get('scan_summary') or {}).get('coverage_universe_count', '')} exposures** over **{(ranking.get('scan_summary') or {}).get('regional_group_count', '')} regionale/stijlbuckets**. Het bord blijft bewust compact.

{opportunity_board(ranking)}

## 5. Belangrijkste risico’s / ontkrachters
1. Olie blijft verhoogd of stijgt opnieuw, waardoor inflatiedruk hoog blijft.
2. De Fed, ECB of BOJ wordt minder marktvriendelijk dan verwacht.
3. Amerikaanse mega-cap marktleiding breekt na een sterke run.
4. Russell 2000 blijft achter en bevestigt dat marktbreedte zwakker is dan zij lijkt.
5. EM verzwakt door een sterkere dollar of hernieuwde grondstoffendruk.
6. Prijs-, ranking-, scorecard-, render- of verzendvalidatie faalt.

## 6. Kernconclusie
- De portefeuille blijft constructief, maar selectief.
- Amerikaanse marktleiding blijft de kernmotor, maar concentratie moet bewaakt worden.
- IWM en EEM blijven gefinancierd, maar staan onder herbeoordeling tegenover duidelijkere uitdagers.
- Inverse instrumenten zijn geen basisscenario-posities, maar de hedgekaart staat klaar als marktbreedte breekt.

## 7. Vermogenscurve en portefeuilleontwikkeling
- Startkapitaal (EUR): {f2(state.get('starting_capital_eur'))}
- Huidige portefeuillewaarde (EUR): {f2(current_nav)}
- Rendement sinds start (%): {f2((current_nav / float(state.get('starting_capital_eur') or 100000.0) - 1.0) * 100.0)}
- Status vermogenscurve: live gevolgd
- Prijsbasis gevraagde slotdatum: {dutch_date(close_date)}
- FX-referentiedatum: {dutch_date(fx_date)}
- Toelichting: posities en NAV zijn herbouwd vanuit de prijs- en statelaag voor de gevraagde slotdatum {dutch_date(close_date)}.

{section7_table(state, output_dir)}

`EQUITY_CURVE_CHART_PLACEHOLDER`

### Performance van verhandelbare proxy’s
Performance wordt berekend op de verhandelbare ETF-proxy’s die voor portefeuillewaardering worden gebruikt. Benchmarkindexprijzen blijven het analyseanker; slotkoersen van verhandelbare proxy’s bepalen marktwaarde, winst/verlies en bijdrage.

{performance_table(state)}

## 8. Regionale en stijlallocatiekaart
{regional_map()}

## 9. Tweede-orde-effectenkaart
- Hogere olieprijzen duwen inflatieverwachtingen omhoog en stellen ruimer beleid verder uit.
- Een later pad voor Fed-renteverlagingen raakt IWM sterker dan QQQ.
- Europa blijft energiegevoeliger dan de VS of Canada.
- Grondstoffensterkte helpt Canada directer dan breed Europa.
- Als Amerikaanse marktleiding verzwakt, activeert RWM waarschijnlijk vóór SH.
- Als dollardruk opnieuw stijgt, wordt EUM relevanter tegenover EEM.

## 10. Beoordeling huidige posities
{current_position_review(state)}

## 11. Beste nieuwe indexkansen
{best_new_opportunities(ranking)}

{breadth_checkpoint(ranking)}

## 12. Portefeuillerotatieplan
| Sluiten | Verlagen | Houden | Toevoegen | Vervangen |
|---|---|---|---|---|
| Geen | Geen | SPY, QQQ | Geen | IWM en EEM blijven onder herbeoordeling |

## 13. Definitieve actietabel
{final_action_table(state)}

## 14. Positiewijzigingen in deze run
| Ticker | Vorig gewicht % | Nieuw gewicht % | Gewichtswijziging % | Uitgevoerde actie | Toelichting |
|---|---:|---:|---:|---|---|
| SPY | {f2(positions(state)[0].get('weight_pct')) if positions(state) else ''} | {f2(positions(state)[0].get('weight_pct')) if positions(state) else ''} | 0.00 | Geen | Aanhouden; overlapreview tegenover QQQ. |
| QQQ | {f2(positions(state)[1].get('weight_pct')) if len(positions(state)) > 1 else ''} | {f2(positions(state)[1].get('weight_pct')) if len(positions(state)) > 1 else ''} | 0.00 | Geen | Aanhouden als sterkste kernpositie. |
| IWM | {f2(positions(state)[2].get('weight_pct')) if len(positions(state)) > 2 else ''} | {f2(positions(state)[2].get('weight_pct')) if len(positions(state)) > 2 else ''} | 0.00 | Geen | Gefinancierd, maar onder herbeoordeling. |
| EEM | {f2(positions(state)[3].get('weight_pct')) if len(positions(state)) > 3 else ''} | {f2(positions(state)[3].get('weight_pct')) if len(positions(state)) > 3 else ''} | 0.00 | Geen | Gefinancierd, maar onder herbeoordeling. |

## 15. Huidige portefeuilleposities en cash
- Startkapitaal (EUR): {f2(state.get('starting_capital_eur'))}
- Belegde marktwaarde (EUR): {f2(invested(state))}
- Cash (EUR): {f2(current_cash)}
- Totale portefeuillewaarde (EUR): {f2(current_nav)}
- Rendement sinds start (%): {f2((current_nav / float(state.get('starting_capital_eur') or 100000.0) - 1.0) * 100.0)}

{holdings_table(state)}

## 16. Continuïteitsinvoer voor de volgende run
**Deze sectie is de canonieke standaardinput voor de volgende run tenzij de gebruiker expliciet iets anders opgeeft.**

### Portefeuilletabel
{continuity_table(state)}

### Beschikbare cash
- Cash %: {f2(current_cash / (current_nav or 1.0) * 100.0)}
- Margegebruik %: 0.00
- Leverage toegestaan: Nee

### Volglijst / dynamisch radargeheugen
- EWJ: sterkste ontwikkelde ex-VS-kandidaat.
- EWC: Canada blijft een echte uitdager.
- FXI: Greater China blijft tactisch relevant.
- RWM, EUM en PSQ blijven defensieve instrumenten, geen basisscenario-longposities.

## 17. Disclaimer
Dit rapport is uitsluitend bedoeld voor informatieve en educatieve doeleinden. Het is geen beleggingsadvies, juridisch advies, fiscaal advies of financieel advies, en vormt geen aanbeveling om effecten te kopen, te verkopen of aan te houden. Beleggen brengt risico’s met zich mee, waaronder het risico op verlies van inleg.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--output-dir", default="output_indices")
    parser.add_argument("--state-path", default="output_indices/index_portfolio_state.json")
    parser.add_argument("--nl-report", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    state = read_json(Path(args.state_path))
    ranking = load_ranking(output_dir, args.token)
    nl_path = Path(args.nl_report) if args.nl_report else output_dir / f"weekly_indices_review_nl_{args.token}.md"
    nl_path.write_text(render_native_nl(state, ranking, output_dir, args.token).rstrip() + "\n", encoding="utf-8")
    print(f"INDEX_NL_NATIVE_RENDER_OK | report={nl_path.name} | token={args.token}")


if __name__ == "__main__":
    main()
