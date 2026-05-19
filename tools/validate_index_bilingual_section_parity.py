#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

SECTION_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$", re.M)
EXPECTED_NL = {
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


def sections(path: Path) -> list[int]:
    return [int(m.group(1)) for m in SECTION_RE.finditer(path.read_text(encoding="utf-8"))]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--en-report", required=True)
    parser.add_argument("--nl-report", required=True)
    args = parser.parse_args()

    en_path = Path(args.en_report)
    nl_path = Path(args.nl_report)
    en_sections = sections(en_path)
    nl_text = nl_path.read_text(encoding="utf-8")
    nl_matches = [(int(m.group(1)), m.group(2).strip()) for m in SECTION_RE.finditer(nl_text)]
    nl_sections = [n for n, _ in nl_matches]

    failures: list[str] = []
    if en_sections != nl_sections:
        failures.append(f"section number mismatch: en={en_sections} nl={nl_sections}")
    for number, title in nl_matches:
        expected = EXPECTED_NL.get(number)
        if expected and title != expected:
            failures.append(f"section {number} title mismatch: got={title!r} expected={expected!r}")

    if failures:
        raise SystemExit("FAIL: bilingual section parity failed: " + "; ".join(failures))
    print(f"INDEX_BILINGUAL_SECTION_PARITY_OK | en={en_path.name} | nl={nl_path.name}")


if __name__ == "__main__":
    main()
