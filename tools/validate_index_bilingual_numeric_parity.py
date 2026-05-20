#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

ISO_DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
DUTCH_DATE_RE = re.compile(
    r"\b(?:maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)\s+\d{1,2}\s+"
    r"(?:januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\s+20\d{2}\b",
    re.I,
)


def f2(value: object) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return ""


def pct(value: object, signed: bool = False) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    sign = "+" if signed and number > 0 else ""
    return f"{sign}{number:.2f}%"


def numeric_variants(value: object, *, allow_integer: bool = False, signed_pct: bool = False) -> list[str]:
    """Return equivalent display formats accepted in EN and NL markdown.

    The English report may use integer share counts (`44`) and comma-formatted
    P/L values (`2,977.78`), while the native NL renderer usually emits `44.00`
    and `2977.78`. These are equivalent for parity purposes.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return []

    variants = {f"{number:.2f}", f"{number:,.2f}"}
    if signed_pct:
        sign = "+" if number > 0 else ""
        variants.add(f"{sign}{number:.2f}%")
        variants.add(f"{sign}{number:,.2f}%")
    if allow_integer and math.isfinite(number) and float(number).is_integer():
        variants.add(str(int(number)))
    return sorted(v for v in variants if v)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def must_contain_any(text: str, needles: list[str], label: str, failures: list[str]) -> None:
    if not needles:
        failures.append(f"missing {label}: no value")
        return
    if not any(needle in text for needle in needles):
        failures.append(f"missing {label}: one of {needles}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--en-report", required=True)
    parser.add_argument("--nl-report", required=True)
    parser.add_argument("--state-path", default="output_indices/index_portfolio_state.json")
    args = parser.parse_args()

    en_text = Path(args.en_report).read_text(encoding="utf-8")
    nl_text = Path(args.nl_report).read_text(encoding="utf-8")
    state = read_json(Path(args.state_path))
    failures: list[str] = []

    core_values = {
        "starting capital": state.get("starting_capital_eur"),
        "portfolio value": state.get("total_portfolio_value_eur"),
        "cash": state.get("cash_eur"),
    }
    for label, value in core_values.items():
        variants = numeric_variants(value)
        must_contain_any(en_text, variants, f"EN {label}", failures)
        must_contain_any(nl_text, variants, f"NL {label}", failures)

    for position in state.get("positions", []) or []:
        proxy = str(position.get("primary_proxy") or "").upper()
        checks = {
            f"{proxy} shares": (position.get("shares"), True, False),
            f"{proxy} latest close": (position.get("latest_proxy_close"), False, False),
            f"{proxy} market value EUR": (position.get("market_value_eur"), False, False),
            f"{proxy} weight": (position.get("weight_pct"), False, False),
        }
        for label, (value, allow_integer, signed_pct) in checks.items():
            variants = numeric_variants(value, allow_integer=allow_integer, signed_pct=signed_pct)
            must_contain_any(en_text, variants, f"EN {label}", failures)
            must_contain_any(nl_text, variants, f"NL {label}", failures)

        perf = position.get("performance") or {}
        perf_checks = {
            f"{proxy} 1w return": (perf.get("one_week_return_pct"), False, True),
            f"{proxy} 1m return": (perf.get("one_month_return_pct"), False, True),
            f"{proxy} 3m return": (perf.get("three_month_return_pct"), False, True),
            f"{proxy} since-entry return": (perf.get("since_entry_return_pct"), False, True),
            f"{proxy} pnl EUR": (perf.get("pnl_eur"), False, False),
            f"{proxy} contribution": (perf.get("contribution_pct"), False, True),
        }
        for label, (value, allow_integer, signed_pct) in perf_checks.items():
            variants = numeric_variants(value, allow_integer=allow_integer, signed_pct=signed_pct)
            must_contain_any(en_text, variants, f"EN {label}", failures)
            must_contain_any(nl_text, variants, f"NL {label}", failures)

    if ISO_DATE_RE.search(nl_text):
        failures.append("NL report still contains raw ISO date")
    if not DUTCH_DATE_RE.search(nl_text):
        failures.append("NL report does not contain a Dutch long date")

    if failures:
        raise SystemExit("FAIL: bilingual numeric parity failed: " + "; ".join(failures[:20]))
    print(f"INDEX_BILINGUAL_STATE_NUMERIC_PARITY_OK | en={Path(args.en_report).name} | nl={Path(args.nl_report).name}")


if __name__ == "__main__":
    main()
