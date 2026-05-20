#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED_HEADINGS = [
    "## 1. Samenvatting",
    "## 2. Portefeuille-acties in één oogopslag",
    "## 7. Vermogenscurve en portefeuilleontwikkeling",
    "## 11. Beste nieuwe indexkansen",
    "## 15. Huidige portefeuilleposities en cash",
    "## 17. Disclaimer",
]

REQUIRED_TERMS = [
    "Nederlandse conceptversie",
    "Prijsbasis gevraagde slotdatum",
    "FX-referentiedatum",
    "Performance van verhandelbare proxy’s",
    "Portefeuillesleeve",
    "Vermogenscurve",
]

FORBIDDEN_DATE_TERMS = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
]

FORBIDDEN_INTERNAL_TERMS = [
    "board_capacity", "near_miss", "ruled_out", "artifact rebuild", "live repo state",
]

FORBIDDEN_BAD_ARTIFACTS = [
    "Houdenings",
    "portfolio NAV",
    "including EUR",
    "rebuilt from the",
    "None this run",
    "Keep QQQ",
    "Test SPY",
    "Force IWM",
    "Higher oil or sticky inflation",
    "Current read",
    "Why it is on the board",
    "Why not on the board yet",
    "Close challenger, not funded",
    "Sluiten challenger, not funded",
    "The portfolio remains constructive",
    "Notes:",
    "Pricing basis close",
]

# Allow financial labels that intentionally remain English-like, such as
# risk-on/risk-off, USD, EM, long, short, hedge, ticker symbols and index names.
SENTENCE_LEVEL_ENGLISH_RESIDUE = [
    re.compile(r"\bportfolio NAV\b"),
    re.compile(r"\bincluding EUR\b"),
    re.compile(r"\brebuilt from the\b"),
    re.compile(r"\bNone this run\b"),
    re.compile(r"\bThe board remains\b"),
    re.compile(r"\bThe scan covers\b"),
    re.compile(r"\bThe portfolio remains\b"),
    re.compile(r"\bCurrent read\b"),
    re.compile(r"\bWhy it is on the board\b"),
    re.compile(r"\bWhy not on the board yet\b"),
    re.compile(r"\bPricing basis close\b"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nl-report", required=True)
    args = parser.parse_args()

    path = Path(args.nl_report)
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            failures.append(f"missing heading: {heading}")
    for term in REQUIRED_TERMS:
        if term not in text:
            failures.append(f"missing required Dutch term: {term}")
    for term in FORBIDDEN_DATE_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", text):
            failures.append(f"English date leakage: {term}")
    for term in FORBIDDEN_INTERNAL_TERMS:
        if term in text:
            failures.append(f"internal term leakage: {term}")
    for term in FORBIDDEN_BAD_ARTIFACTS:
        if term in text:
            failures.append(f"bad Dutch localization artifact: {term}")
    for pattern in SENTENCE_LEVEL_ENGLISH_RESIDUE:
        if pattern.search(text):
            failures.append(f"English residue pattern: {pattern.pattern}")

    if failures:
        raise SystemExit("FAIL: Dutch language contract failed for " + path.name + ": " + "; ".join(failures))
    print(f"INDEX_NL_LANGUAGE_OK | report={path.name}")


if __name__ == "__main__":
    main()
