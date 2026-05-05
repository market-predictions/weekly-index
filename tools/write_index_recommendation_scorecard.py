#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any

REPORT_RE = re.compile(r"^weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")

FIELDNAMES = [
    "report_date",
    "ticker",
    "exposure",
    "weight_pct",
    "shares",
    "current_price_local",
    "currency",
    "market_value_eur",
    "total_score",
    "suggested_action",
    "conviction_tier",
    "portfolio_role",
    "fresh_cash_test",
    "would_initiate_today",
    "would_initiate_at_current_weight",
    "thesis_score",
    "implementation_score",
    "replaceable_status",
    "weeks_replaceable",
    "best_alternative",
    "alternative_score",
    "contribution_quality",
    "factor_overlap_flag",
    "breadth_concentration_flag",
    "inverse_hedge_candidate",
    "cash_policy_flag",
    "required_next_action",
    "override_reason",
    "discipline_flags",
    "source_report",
]

ALT_BY_TICKER = {
    "SPY": "VOO/QUAL/IEFA",
    "QQQ": "QQQM/QUAL/SPY",
    "IWM": "VTWO/RWM",
    "EEM": "VWO/EUM/INDA",
    "EWJ": "DXJ/FEZ",
    "EWG": "FEZ/EZU",
    "FEZ": "VGK/EWG",
    "EWU": "ISF.L/FEZ",
    "EWL": "CSSMI.SW/FEZ",
    "EWC": "XIU.TO/SPY",
    "EWA": "STW.AX/EWC",
}

INVERSE_BY_TICKER = {
    "SPY": "SH",
    "QQQ": "PSQ",
    "IWM": "RWM",
    "EEM": "EUM",
    "FEZ": "EFZ",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Write Weekly Index recommendation scorecard from latest report")
    p.add_argument("--output-dir", default="output_indices")
    p.add_argument("--check-only", action="store_true")
    return p.parse_args()


def clean(value: str | None) -> str:
    text = value or ""
    text = re.sub(r".*?", "", text)
    text = text.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def safe_float(value: str | None) -> float | None:
    raw = clean(value).replace(",", "").replace("%", "")
    if not raw or raw in {"-", "—", "TBD"}:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def report_sort_key(path: Path) -> tuple[str, int]:
    match = REPORT_RE.match(path.name)
    if not match:
        return ("", -1)
    return (match.group(1), int(match.group(2) or "0"))


def latest_report_file(output_dir: Path) -> Path:
    reports = sorted([p for p in output_dir.glob("weekly_indices_review_*.md") if REPORT_RE.match(p.name)], key=report_sort_key)
    if not reports:
        raise FileNotFoundError("No weekly_indices_review_*.md file found")
    return reports[-1]


def parse_report_date(md_text: str, report_path: Path) -> str:
    match = re.search(r"^#\s+Weekly Indices Review(?:\s+(\d{4}-\d{2}-\d{2}))?", md_text, flags=re.MULTILINE)
    if match and match.group(1):
        return match.group(1)
    token = REPORT_RE.match(report_path.name).group(1)  # type: ignore[union-attr]
    return f"20{token[0:2]}-{token[2:4]}-{token[4:6]}"


def extract_section(md_text: str, number: int) -> list[str]:
    lines = md_text.splitlines()
    start = None
    end = None
    for i, line in enumerate(lines):
        if line.strip().startswith(f"## {number}."):
            start = i + 1
            continue
        if start is not None and line.strip().startswith("## "):
            end = i
            break
    if start is None:
        return []
    return lines[start:end or len(lines)]


def is_table_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|")


def is_separator(line: str) -> bool:
    s = line.strip().strip("|").replace("-", "").replace(":", "").replace(" ", "")
    return s == ""


def parse_first_table(lines: list[str]) -> list[dict[str, str]]:
    block: list[str] = []
    capture = False
    for line in lines:
        if is_table_line(line):
            block.append(line)
            capture = True
        elif capture:
            break
    if len(block) < 2:
        return []
    headers = [clean(c).lower() for c in block[0].strip().strip("|").split("|")]
    rows = []
    for line in block[1:]:
        if is_separator(line):
            continue
        cells = [clean(c) for c in line.strip().strip("|").split("|")]
        row = {headers[i]: cells[i] if i < len(cells) else "" for i in range(len(headers))}
        rows.append(row)
    return rows


def map_by_ticker(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out = {}
    for row in rows:
        ticker = clean(row.get("ticker") or row.get("implementation proxy") or row.get("primary proxy") or "").upper()
        if ticker and ticker != "CASH":
            out[ticker] = row
    return out


def parse_replaceables(md_text: str) -> set[str]:
    section = "\n".join(extract_section(md_text, 2))
    match = re.search(r"###\s*Hold but replaceable\s*(.*?)(?:\n###|\Z)", section, flags=re.I | re.S)
    if not match:
        return set()
    return {token for token in re.findall(r"\b[A-Z][A-Z0-9.\-]{1,11}\b", match.group(1)) if token not in {"NONE", "TBD"}}


def previous_scorecard(output_dir: Path) -> dict[str, dict[str, str]]:
    path = output_dir / "index_recommendation_scorecard.csv"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {row.get("ticker", "").upper(): row for row in rows if row.get("ticker")}


def classify_fresh_cash(total_score: float | None, replaceable: bool, ticker: str) -> tuple[str, str, str]:
    if total_score is None:
        if replaceable:
            return "Unresolved / under review", "Unresolved", "No"
        if ticker in {"SPY", "QQQ"}:
            return "Hold", "Yes", "Yes"
        return "Unresolved", "Unresolved", "Unresolved"
    if total_score >= 4.2 and not replaceable:
        return "Add/Hold", "Yes", "Yes"
    if total_score >= 3.6 and not replaceable:
        return "Hold", "Yes", "Yes"
    if total_score >= 3.0:
        return "Smaller / under review", "Smaller", "No"
    return "Reduce / replace", "No", "No"


def factor_flag(ticker: str, weight: float | None) -> str:
    if ticker in {"SPY", "QQQ"}:
        return "U.S. mega-cap / growth-beta overlap"
    if ticker == "IWM":
        return "Small-cap financing sensitivity"
    if ticker == "EEM":
        return "Dollar / EM risk sensitivity"
    if ticker in {"FEZ", "EWG", "EWU", "EWL"}:
        return "Europe regional concentration"
    return ""


def contribution_quality(weight: float | None, action: str) -> str:
    if weight is None:
        return "Unresolved"
    if "replace" in action.lower() or "reduce" in action.lower():
        return "Opportunity-cost review"
    if weight >= 20:
        return "Core contributor / concentration review"
    if weight >= 10:
        return "Meaningful contributor"
    return "Satellite contributor"


def required_action(ticker: str, replaceable: bool, weeks: int, action: str, total_score: float | None) -> str:
    if replaceable and weeks >= 2:
        return "Force direct alternative duel; upgrade, reduce, replace, or close"
    if replaceable:
        return "Hold under review; name best alternative and trigger"
    if ticker == "IWM":
        return "Monitor breadth; compare against RWM if deterioration triggers"
    if ticker == "EEM":
        return "Monitor dollar pressure; compare against EUM if EM breaks"
    if total_score is not None and total_score >= 4.2:
        return "Eligible for add if cash policy allows"
    return "Hold"


def build_rows(output_dir: Path, report_path: Path, md_text: str) -> list[dict[str, str]]:
    report_date = parse_report_date(md_text, report_path)
    s13 = map_by_ticker(parse_first_table(extract_section(md_text, 13)))
    s15_rows = parse_first_table(extract_section(md_text, 15))
    replaceables = parse_replaceables(md_text)
    previous = previous_scorecard(output_dir)
    rows = []
    for h in s15_rows:
        ticker = clean(h.get("ticker")).upper()
        if not ticker or ticker == "CASH":
            continue
        action_row = s13.get(ticker, {})
        exposure = clean(h.get("public index / exposure") or action_row.get("public index / exposure") or ticker)
        weight = safe_float(h.get("weight %") or action_row.get("target weight"))
        total_score = safe_float(action_row.get("total score"))
        action = clean(action_row.get("suggested action")) or clean(h.get("stance")) or "Hold"
        replaceable = ticker in replaceables or "replace" in action.lower()
        prev_weeks = int(safe_float((previous.get(ticker) or {}).get("weeks_replaceable")) or 0)
        weeks = prev_weeks + 1 if replaceable else 0
        fresh_cash, would_today, would_weight = classify_fresh_cash(total_score, replaceable, ticker)
        thesis_score = total_score if total_score is not None else (4.2 if ticker in {"SPY", "QQQ"} else 3.3)
        implementation_score = thesis_score - (0.35 if replaceable else 0.0)
        discipline_flags = []
        if replaceable:
            discipline_flags.append("replaceable")
        if ticker in {"SPY", "QQQ"}:
            discipline_flags.append("factor_overlap")
        if ticker in {"IWM", "EEM"}:
            discipline_flags.append("breadth_or_dollar_review")
        inverse = INVERSE_BY_TICKER.get(ticker, "")
        rows.append({
            "report_date": report_date,
            "ticker": ticker,
            "exposure": exposure,
            "weight_pct": "" if weight is None else f"{weight:.2f}",
            "shares": clean(h.get("shares")),
            "current_price_local": clean(h.get("price (local)")),
            "currency": clean(h.get("currency")),
            "market_value_eur": clean(h.get("market value (eur)")),
            "total_score": "" if total_score is None else f"{total_score:.2f}",
            "suggested_action": action,
            "conviction_tier": clean(action_row.get("conviction tier")),
            "portfolio_role": clean(action_row.get("portfolio role")) or exposure,
            "fresh_cash_test": fresh_cash,
            "would_initiate_today": would_today,
            "would_initiate_at_current_weight": would_weight,
            "thesis_score": f"{max(1.0, min(5.0, thesis_score)):.2f}",
            "implementation_score": f"{max(1.0, min(5.0, implementation_score)):.2f}",
            "replaceable_status": "Hold under review" if replaceable else "None",
            "weeks_replaceable": str(weeks),
            "best_alternative": ALT_BY_TICKER.get(ticker, ""),
            "alternative_score": "",
            "contribution_quality": contribution_quality(weight, action),
            "factor_overlap_flag": factor_flag(ticker, weight),
            "breadth_concentration_flag": "Review concentration if U.S. funded weight >40% or non-U.S. breadth remains weak",
            "inverse_hedge_candidate": inverse,
            "cash_policy_flag": "Review if cash >3% and actionable lanes exist",
            "required_next_action": required_action(ticker, replaceable, weeks, action, total_score),
            "override_reason": "Required if Hold persists despite discipline flags" if discipline_flags and action.lower() == "hold" else "",
            "discipline_flags": ";".join(discipline_flags),
            "source_report": report_path.name,
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    report_path = latest_report_file(output_dir)
    md_text = report_path.read_text(encoding="utf-8")
    rows = build_rows(output_dir, report_path, md_text)
    if not rows:
        raise RuntimeError(f"Could not derive index recommendation scorecard rows from {report_path.name}")
    path = output_dir / "index_recommendation_scorecard.csv"
    flagged = sum(1 for row in rows if row.get("discipline_flags"))
    if args.check_only:
        print(f"INDEX_RECOMMENDATION_SCORECARD_DERIVATION_OK | report={report_path.name} | rows={len(rows)} | flagged={flagged} | scorecard={path.name}")
        return
    write_csv(path, rows)
    print(f"INDEX_RECOMMENDATION_SCORECARD_OK | report={report_path.name} | rows={len(rows)} | flagged={flagged} | scorecard={path.name}")


if __name__ == "__main__":
    main()
