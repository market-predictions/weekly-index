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

# Exact replacements only. Avoid short generic words such as Hold/Close because
# those can corrupt terms like Holdings or Close challenger.
EXACT_REPLACEMENTS = [
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
    ("Regional / style bucket", "Regio / stijlbucket"),
    ("Current view", "Huidige visie"),
    ("Current read", "Huidige lezing"),
    ("Comment", "Toelichting"),
    ("Shares", "Aandelen"),
    ("Price (local)", "Prijs (lokaal)"),
    ("Currency", "Valuta"),
    ("Market value (local)", "Marktwaarde (lokaal)"),
    ("Market value (EUR)", "Marktwaarde (EUR)"),
    ("Decision", "Besluit"),
    ("Required trigger", "Vereiste trigger"),
    ("Public index / exposure", "Publieke index / exposure"),
    ("Why it is on the board", "Reden voor opname"),
    ("Why not on the board yet", "Waarom nog niet op het bord"),
    ("Proxy eligibility", "Proxy-geschiktheid"),
    ("Published?", "Gepubliceerd?"),
    ("Challenger score", "Challenger-score"),
    ("Strongest candidate", "Sterkste kandidaat"),
    ("Candidate count", "Aantal kandidaten"),
    ("Eligible proxies", "Geschikte proxy’s"),
    ("Current exposure", "Huidige exposure"),
    ("Current proxy", "Huidige proxy"),
    ("Alternative / hedge", "Alternatief / hedge"),
    ("Alternative proxy", "Alternatieve proxy"),
    ("Long alternative", "Long-alternatief"),
    ("Defensive / inverse", "Defensief / inverse"),
    ("Best Defensive / Inverse Opportunities", "Beste defensieve / inverse kansen"),
    ("Long-side Opportunities", "Long-kansen"),
    ("Alternative Duel Table", "Alternatieve dueltabel"),
    ("Breadth checkpoint by regional bucket", "Marktbreedtecheck per regionale bucket"),
    ("Universe scan checkpoint", "Universumscan-checkpoint"),
    ("Add", "Toevoegen"),
    ("Reduce", "Verlagen"),
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

EXACT_SENTENCE_REPLACEMENTS = [
    ("Risk-on narrow US mega-cap leadership", "Risk-on met smalle Amerikaanse mega-cap marktleiding"),
    ("72% confidence", "72% vertrouwen"),
    ("Elevated USD / policy-friction risk", "Verhoogd USD- / beleidsfrictierisico"),
    ("Keep EM, China, Korea/Taiwan and commodity-sensitive regions on a higher evidence hurdle until USD pressure eases.", "Houd EM, China, Korea/Taiwan en grondstofgevoelige regio’s op een hogere bewijsdrempel totdat de USD-druk afneemt."),
    ("Nasdaq leadership is stronger than small-cap breadth, so risk appetite remains narrow rather than broad.", "Nasdaq-leiderschap is sterker dan small-cap marktbreedte; de risicobereidheid blijft dus smal in plaats van breed."),
    ("Do not treat narrow U.S. leadership as full global breadth confirmation.", "Behandel smalle Amerikaanse marktleiding niet als volledige bevestiging van wereldwijde marktbreedte."),
    ("keep QQQ as the strongest earned sleeve, keep SPY under concentration review, and force IWM and EEM through named long-alternative and defensive-hedge duels before any new capital is assigned.", "houd QQQ als sterkste verdiende sleeve, houd SPY onder concentratiecontrole en dwing IWM en EEM door expliciete long-alternatief- en defensieve hedge-duels voordat nieuw kapitaal wordt toegewezen."),
    ("None this run. Cash remains available, but no challenger clears the full pricing, regime and relative-strength hurdle yet.", "Geen toevoeging deze run. Cash blijft beschikbaar, maar nog geen enkele uitdager haalt de volledige drempel voor prijs, regime en relatieve sterkte."),
    ("None until the direct alternative-duel evidence produces a cleaner replacement or hedge trigger.", "Geen verlaging totdat het directe alternatief-duel een schonere vervanging of hedge-trigger oplevert."),
    ("None this run.", "Geen actie deze run."),
    ("Japan large cap via EWJ", "Japan large cap via EWJ"),
    ("Canada broad via EWC", "Canada breed via EWC"),
    ("Greater China large cap via FXI", "Greater China large cap via FXI"),
    ("Keep QQQ as the strongest core holding while leadership remains intact.", "Houd QQQ als sterkste kernpositie zolang het leiderschap intact blijft."),
    ("Test SPY against QQQ overlap so U.S. exposure is not mistaken for full diversification.", "Test SPY op overlap met QQQ, zodat Amerikaanse exposure niet wordt verward met volledige diversificatie."),
    ("Force IWM and EEM through long-alternative and defensive/inverse comparisons before adding capital.", "Dwing IWM en EEM door long-alternatief- en defensieve/inverse vergelijkingen voordat extra kapitaal wordt toegevoegd."),
    ("Higher oil or sticky inflation delays easier policy and keeps pressure on weak breadth.", "Hogere olieprijzen of hardnekkige inflatie vertragen ruimer beleid en houden druk op zwakke marktbreedte."),
    ("SPY and QQQ remain a concentration cluster, not a diversified global allocation.", "SPY en QQQ blijven een concentratiecluster, geen gediversifieerde wereldwijde allocatie."),
    ("IWM and EEM stay under review until breadth, USD and relative-strength evidence improve.", "IWM en EEM blijven onder herbeoordeling totdat marktbreedte, USD-beeld en relatieve sterkte verbeteren."),
    ("Still resilient; AI and semis continue to lead", "Nog altijd veerkrachtig; AI en halfgeleiders blijven leiden"),
    ("Supports QQQ and keeps SPY valid", "Ondersteunt QQQ en houdt SPY valide"),
    ("Higher oil is reviving inflation concerns", "Hogere olieprijzen brengen inflatiezorgen terug"),
    ("Keeps pressure on weak-margin cyclicals", "Houdt druk op cyclische waarden met lage marges"),
    ("Fed-cut expectations have been pushed back", "Verwachtingen voor Fed-renteverlagingen zijn naar achteren geschoven"),
    ("Less friendly for small caps and rate-sensitive beta", "Minder gunstig voor small caps en rentegevoelige beta"),
    ("Flat-to-weaker tape under oil and geopolitical strain", "Vlak tot zwakker koersbeeld door olie- en geopolitieke druk"),
    ("Europe stays below the cut line for now", "Europa blijft voorlopig onder de selectielijn"),
    ("Better relative setup than Europe broad", "Betere relatieve setup dan breed Europa"),
    ("EWJ remains one of the most credible add candidates", "EWJ blijft een van de meest geloofwaardige toevoegingskandidaten"),
    ("Commodity support is improving the case", "Grondstoffensteun verbetert de casus"),
    ("EWC remains a real challenger, not filler", "EWC blijft een echte uitdager, geen opvulling"),
    ("Still investable, but more exposed to dollar/oil stress than U.S. leadership", "Nog steeds belegbaar, maar gevoeliger voor dollar- en oliedruk dan Amerikaanse marktleiding"),
    ("EEM must pass a stricter review versus alternatives", "EEM moet een strengere beoordeling tegenover alternatieven doorstaan"),
    ("The scan covers", "De scan omvat"),
    ("regional/style buckets", "regionale/stijlbuckets"),
    ("The board remains compact by design; broader coverage is shown later in the universe checkpoint.", "Het bord blijft bewust compact; bredere dekking staat verderop in het universum-checkpoint."),
    ("The board remains intentionally compact.", "Het bord blijft bewust compact."),
    ("The strongest omitted regional challenger this run is", "De sterkste weggelaten regionale uitdager deze run is"),
    ("which remains close enough to matter without displacing a higher-ranked funded exposure.", "die dicht genoeg bij de selectie blijft om relevant te zijn zonder een hoger gerangschikte gefinancierde exposure te verdringen."),
    ("Oil remains elevated or spikes again, keeping inflation pressure high.", "Olie blijft verhoogd of stijgt opnieuw, waardoor inflatiedruk hoog blijft."),
    ("The Fed, ECB, or BOJ turns less market-friendly than expected.", "De Fed, ECB of BOJ wordt minder marktvriendelijk dan verwacht."),
    ("U.S. mega-cap leadership finally cracks after a record run.", "Amerikaanse mega-cap marktleiding breekt na een sterke run."),
    ("Russell 2000 continues to lag and confirms that breadth is weaker than it looks.", "Russell 2000 blijft achter en bevestigt dat marktbreedte zwakker is dan zij lijkt."),
    ("EM weakens under a stronger dollar or renewed commodity stress.", "EM verzwakt door een sterkere dollar of hernieuwde grondstoffendruk."),
    ("Pricing, ranking, scorecard, render, or send validation fails.", "Prijs-, ranking-, scorecard-, render- of verzendvalidatie faalt."),
    ("The portfolio remains constructive but selective.", "De portefeuille blijft constructief, maar selectief."),
    ("U.S. leadership remains the core engine, but concentration must be watched.", "Amerikaanse marktleiding blijft de kernmotor, maar concentratie moet bewaakt worden."),
    ("IWM and EEM remain funded but under review versus clearer challengers.", "IWM en EEM blijven gefinancierd, maar staan onder herbeoordeling tegenover duidelijkere uitdagers."),
    ("Inverse instruments are not base-case positions, but the hedge map is ready if breadth breaks.", "Inverse instrumenten zijn geen basisscenario-posities, maar de hedgekaart staat klaar als marktbreedte breekt."),
    ("Live tracked", "Live gevolgd"),
    ("Pricing basis close", "Prijsbasis slotkoers"),
    ("Notes:", "Toelichting:"),
    ("Holdings and NAV are rebuilt from the pricing/state layer for the requested close date", "Posities en NAV zijn herbouwd vanuit de prijs- en statelaag voor de gevraagde slotdatum"),
    ("Overweight", "Overwogen"),
    ("Neutral-positive", "Neutraal-positief"),
    ("Under active review", "Onder actieve herbeoordeling"),
    ("Underweight", "Onderwogen"),
    ("Lower priority", "Lagere prioriteit"),
    ("Positive", "Positief"),
    ("Tactical watch", "Tactische watchlist"),
    ("QQQ remains the strongest sleeve", "QQQ blijft de sterkste sleeve"),
    ("SPY still works, but overlap must be tested", "SPY werkt nog, maar overlap moet worden getest"),
    ("IWM is funded, but no longer a passive hold", "IWM is gefinancierd, maar niet langer een passieve hold"),
    ("Oil and geopolitical sensitivity remain a drag", "Olie- en geopolitieke gevoeligheid blijven een rem"),
    ("Not yet strong enough versus Japan or Canada", "Nog niet sterk genoeg tegenover Japan of Canada"),
    ("Defensive quality, but not top-ranked yet", "Defensieve kwaliteit, maar nog niet topgerangschikt"),
    ("Canada remains a real challenger", "Canada blijft een echte uitdager"),
    ("Strongest developed ex-U.S. lane", "Sterkste ontwikkelde ex-VS-sleeve"),
    ("FXI remains a real breadth candidate", "FXI blijft een echte marktbreedtekandidaat"),
    ("Still interesting, but not top-ranked today", "Nog interessant, maar vandaag niet topgerangschikt"),
    ("EEM must beat more selective alternatives", "EEM moet selectievere alternatieven verslaan"),
    ("Higher oil pushes inflation expectations higher and keeps easier policy further away.", "Hogere olieprijzen duwen inflatieverwachtingen omhoog en stellen ruimer beleid verder uit."),
    ("A later Fed-cut path matters more for IWM than for QQQ.", "Een later pad voor Fed-renteverlagingen raakt IWM sterker dan QQQ."),
    ("Europe remains more energy-sensitive than the U.S. or Canada.", "Europa blijft energiegevoeliger dan de VS of Canada."),
    ("Commodity strength helps Canada more directly than Europe broad.", "Grondstoffensterkte helpt Canada directer dan breed Europa."),
    ("If U.S. leadership finally weakens, RWM likely activates before SH.", "Als Amerikaanse marktleiding verzwakt, activeert RWM waarschijnlijk vóór SH."),
    ("If dollar pressure rises again, EUM becomes more relevant against EEM.", "Als dollardruk opnieuw stijgt, wordt EUM relevanter tegenover EEM."),
    ("Would initiate today", "Zou vandaag instappen"),
    ("Would initiate at current weight", "Zou instappen op huidig gewicht"),
    ("Thesis score", "Thesescore"),
    ("Implementation score", "Implementatiescore"),
    ("Best alternative", "Beste alternatief"),
    ("Required next action", "Vereiste volgende actie"),
    ("Yes, but only after explicit overlap review versus QQQ", "Ja, maar alleen na expliciete overlapbeoordeling versus QQQ"),
    ("Yes, but only within concentration limits", "Ja, maar alleen binnen concentratielimieten"),
    ("Yes, while mega-cap leadership remains intact", "Ja, zolang mega-cap marktleiding intact blijft"),
    ("Yes", "Ja"),
    ("No", "Nee"),
    ("Smaller / Unresolved", "Kleiner / onopgelost"),
    ("test whether SPY still diversifies the book or mainly duplicates U.S. mega-cap growth beta.", "test of SPY de portefeuille nog diversifieert of vooral Amerikaanse mega-cap groeibeta dupliceert."),
    ("keep as top core holding unless leadership clearly breaks.", "houd als kernpositie zolang marktleiding niet duidelijk breekt."),
    ("force direct alternative duel; upgrade, reduce, replace, or close.", "dwing een direct alternatief-duel af; verhogen, verlagen, vervangen of sluiten."),
    ("It improves breadth and remains close enough to the live board to stay visible in the report.", "Dit verbetert de marktbreedte en blijft dicht genoeg bij het live bord om zichtbaar te blijven in het rapport."),
    ("Ranks well internally but remains just below the current publication cutoff.", "Scoort intern goed, maar blijft net onder de huidige publicatiedrempel."),
    ("Strong challenger, not yet funded", "Sterke kandidaat, nog niet gefinancierd"),
    ("Lower priority this run", "Lagere prioriteit deze run"),
    ("Included on the board", "Opgenomen op het bord"),
    ("Published", "Gepubliceerd"),
    ("Funded", "Gefinancierd"),
    ("Surfaced", "Gepubliceerd"),
]

REGEX_REPLACEMENTS = [
    (
        re.compile(r"portfolio NAV is (EUR [0-9,]+\.\d+), including (EUR [0-9,]+\.\d+) cash, rebuilt from the (.*?) close and FX-referentiedatum (.*?)\."),
        r"portefeuillewaarde is \1, inclusief \2 cash, herbouwd op basis van de slotkoers van \3 en FX-referentiedatum \4.",
    ),
    (
        re.compile(r"De scan omvat \*\*(\d+) exposures\*\* over \*\*(\d+) regionale/stijlbuckets\*\*\."),
        r"De scan omvat **\1 exposures** over **\2 regionale/stijlbuckets**.",
    ),
    (
        re.compile(r"^\s*1\.\s*Keep\s+QQQ.*$", re.M),
        "1. Houd QQQ als sterkste kernpositie zolang het leiderschap intact blijft.",
    ),
    (
        re.compile(r"^\s*2\.\s*Test\s+SPY.*$", re.M),
        "2. Test SPY op overlap met QQQ, zodat Amerikaanse exposure niet wordt verward met volledige diversificatie.",
    ),
    (
        re.compile(r"^\s*3\.\s*Force\s+IWM.*$", re.M),
        "3. Dwing IWM en EEM door long-alternatief- en defensieve/inverse vergelijkingen voordat extra kapitaal wordt toegevoegd.",
    ),
]

BAD_ARTIFACT_FIXUPS = [
    ("Houdenings", "Posities"),
    ("Sluiten challenger, not funded", "Sterke kandidaat, nog niet gefinancierd"),
    ("Close challenger, not funded", "Sterke kandidaat, nog niet gefinancierd"),
    ("Current status", "Huidige status"),
    ("Candidate", "Kandidaat"),
    ("Underlying", "Onderliggende waarde"),
    ("Short thesis", "Short-these"),
    ("Trigger", "Trigger"),
    ("Invalidation", "Ontkrachting"),
    ("Max role", "Maximale rol"),
    ("These instruments are defensive tools only. They are not part of the base-case long allocation.", "Deze instrumenten zijn uitsluitend defensieve instrumenten. Ze maken geen deel uit van de basisscenario-longallocatie."),
]


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


def apply_exact_replacements(text: str) -> str:
    for source, target in HEADER_REPLACEMENTS.items():
        text = text.replace(source, target)
    for source, target in sorted(EXACT_REPLACEMENTS + EXACT_SENTENCE_REPLACEMENTS, key=lambda x: len(x[0]), reverse=True):
        text = text.replace(source, target)
    return text


def apply_regex_replacements(text: str) -> str:
    for pattern, replacement in REGEX_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text


def apply_table_action_replacements(text: str) -> str:
    text = re.sub(r"\|\s*Add\s*\|", "| Toevoegen |", text)
    text = re.sub(r"\|\s*Hold\s*\|", "| Houden |", text)
    text = re.sub(r"\|\s*Hold but replaceable\s*\|", "| Houden, maar vervangbaar |", text)
    text = re.sub(r"\|\s*Reduce\s*\|", "| Verlagen |", text)
    text = re.sub(r"\|\s*Close\s*\|", "| Sluiten |", text)
    return text


def localize_dates(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return dutch_date(match.group(1))
    return re.sub(r"\b(20\d{2}-\d{2}-\d{2})\b", repl, text)


def apply_bad_artifact_fixups(text: str) -> str:
    for source, target in BAD_ARTIFACT_FIXUPS:
        text = text.replace(source, target)
    return text


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
    text = apply_table_action_replacements(text)
    text = apply_exact_replacements(text)
    text = localize_dates(text)
    text = apply_regex_replacements(text)
    text = apply_bad_artifact_fixups(text)
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
