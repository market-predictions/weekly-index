#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def must_contain(text: str, needle: str, label: str, failures: list[str]) -> None:
    if needle not in text:
        failures.append(f"missing {label}: {needle}")


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

    # State-aware parity: the Dutch native renderer does not need to duplicate
    # every incidental English report number, but it must preserve all portfolio
    # authority numbers from the shared state.
    core_values = {
        "starting capital": f2(state.get("starting_capital_eur")),
        "portfolio value": f2(state.get("total_portfolio_value_eur")),
        "cash": f2(state.get("cash_eur")),
    }
    for label, value in core_values.items():
        must_contain(en_text, value, f"EN {label}", failures)
        must_contain(nl_text, value, f"NL {label}", failures)

    for position in state.get("positions", []) or []:
        proxy = str(position.get("primary_proxy") or "").upper()
        for label, value in {
            f"{proxy} shares": f2(position.get("shares")),
            f"{proxy} latest close": f2(position.get("latest_proxy_close")),
            f"{proxy} market value EUR": f2(position.get("market_value_eur")),
            f"{proxy} weight": f2(position.get("weight_pct")),
        }.items():
            must_contain(en_text, value, f"EN {label}", failures)
            must_contain(nl_text, value, f"NL {label}", failures)
        perf = position.get("performance") or {}
        for label, value in {
            f"{proxy} 1w return": pct(perf.get("one_week_return_pct"), signed=True),
            f"{proxy} 1m return": pct(perf.get("one_month_return_pct"), signed=True),
            f"{proxy} 3m return": pct(perf.get("three_month_return_pct"), signed=True),
            f"{proxy} since-entry return": pct(perf.get("since_entry_return_pct"), signed=True),
            f"{proxy} pnl EUR": f2(perf.get("pnl_eur")),
            f"{proxy} contribution": pct(perf.get("contribution_pct"), signed=True),
        }.items():
            must_contain(en_text, value, f"EN {label}", failures)
            must_contain(nl_text, value, f"NL {label}", failures)

    # Date localization must be present in NL and raw ISO date should stay out.
    if ISO_DATE_RE.search(nl_text):
        failures.append("NL report still contains raw ISO date")
    if not DUTCH_DATE_RE.search(nl_text):
        failures.append("NL report does not contain a Dutch long date")

    if failures:
        raise SystemExit("FAIL: bilingual numeric parity failed: " + "; ".join(failures[:20]))
    print(f"INDEX_BILINGUAL_STATE_NUMERIC_PARITY_OK | en={Path(args.en_report).name} | nl={Path(args.nl_report).name}")


if __name__ == "__main__":
    main()
