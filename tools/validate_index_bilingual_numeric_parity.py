#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

# Keep this intentionally broad for the first markdown-only phase. It catches
# accidental numeric drift while tolerating translated labels.
NUMBER_RE = re.compile(r"(?<![A-Za-z0-9])[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?%?(?![A-Za-z0-9])")


def numbers(text: str) -> list[str]:
    return NUMBER_RE.findall(text)


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
