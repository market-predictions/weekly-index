#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

# Numeric parity should protect investment and portfolio values, not punish
# required date localization. The Dutch report intentionally turns ISO dates
# such as 2026-05-18 into maandag 18 mei 2026. Strip dates before extracting
# numeric tokens.
NUMBER_RE = re.compile(r"(?<![A-Za-z0-9])[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?%?(?![A-Za-z0-9])")
ISO_DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
DUTCH_DATE_RE = re.compile(
    r"\b(?:maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)\s+\d{1,2}\s+"
    r"(?:januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\s+20\d{2}\b",
    re.I,
)
EN_LONG_DATE_RE = re.compile(
    r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+\d{1,2}\s+"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d{2}\b",
    re.I,
)
NL_SHORT_DATE_RE = re.compile(
    r"\b\d{1,2}\s+(?:januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\s+20\d{2}\b",
    re.I,
)


def strip_dates(text: str) -> str:
    text = ISO_DATE_RE.sub(" DATE ", text)
    text = DUTCH_DATE_RE.sub(" DATE ", text)
    text = EN_LONG_DATE_RE.sub(" DATE ", text)
    text = NL_SHORT_DATE_RE.sub(" DATE ", text)
    return text


def strip_nonfinancial_number_context(text: str) -> str:
    """Remove numeric contexts that are intentionally language/layout metadata.

    Section numbers, file tokens in titles and image placeholders are checked by
    other validators. This validator focuses on financial numeric parity.
    """
    text = re.sub(r"^##\s+\d+\.\s+.*$", " SECTION ", text, flags=re.M)
    text = re.sub(r"weekly_indices_review(?:_nl)?_\d{6}\b", " REPORT_FILE ", text)
    return text


def normalized_text(text: str) -> str:
    return strip_nonfinancial_number_context(strip_dates(text))


def numbers(text: str) -> list[str]:
    return NUMBER_RE.findall(normalized_text(text))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--en-report", required=True)
    parser.add_argument("--nl-report", required=True)
    args = parser.parse_args()

    en_path = Path(args.en_report)
    nl_path = Path(args.nl_report)
    en_numbers = numbers(en_path.read_text(encoding="utf-8"))
    nl_numbers = numbers(nl_path.read_text(encoding="utf-8"))

    if en_numbers != nl_numbers:
        first_diff = None
        for idx, (en, nl) in enumerate(zip(en_numbers, nl_numbers), start=1):
            if en != nl:
                first_diff = f"first_diff_at={idx} en={en!r} nl={nl!r}"
                break
        if first_diff is None:
            first_diff = f"length_diff en={len(en_numbers)} nl={len(nl_numbers)}"
        raise SystemExit(
            "FAIL: bilingual numeric parity failed: "
            + first_diff
            + f" | en_count={len(en_numbers)} nl_count={len(nl_numbers)}"
        )

    print(f"INDEX_BILINGUAL_NUMERIC_PARITY_OK | en={en_path.name} | nl={nl_path.name} | numbers={len(en_numbers)}")


if __name__ == "__main__":
    main()
