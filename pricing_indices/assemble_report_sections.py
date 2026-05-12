from __future__ import annotations

import argparse
import csv
import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

SECTION4_NAME = "Index Opportunity Board"
SECTION7_NAME = "Equity Curve and Portfolio Development"
SECTION11_NAME = "Best New Index Opportunities"
SECTION15_NAME = "Current Portfolio Holdings and Cash"
SECTION16_NAME = "Continuity Input for Next Run"
REPORT_RE = re.compile(r"weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")
PLAN_RE = re.compile(r"index_recommendation_plan_(\d{6})(?:_(\d{2}))?\.json$")

DISPLAY_NAME_OVERRIDES = {
    "us_large_cap": "S&P 500",
    "us_tech_leadership": "Nasdaq 100",
    "us_small_cap": "Russell 2000",
    "em_broad": "Emerging Markets broad",
    "japan_equities": "Japan large-cap equities",
    "germany_cyclicals": "Germany cyclical equities",
    "europe_large_cap": "Europe broad large-cap equities",
}

STATUS_LABELS = {
    "surfaced": "Published",
    "considered": "Reviewed",
    "near_miss": "Close challenger, not funded",
    "ruled_out": "Lower priority this run",
    "published": "Published",
}

REASON_LABELS = {
    "published": "Included on the board",
    "strong_challenger_not_published": "Strong challenger, not yet funded",
    "board_capacity": "Kept off the compact board by stronger candidates",
    "weak_relative_strength": "Relative strength not strong enough yet",
    "fragile_macro_alignment": "Macro timing not strong enough yet",
    "insufficient_immediate_priority": "Not urgent enough for capital this week",
    "below_board_cutoff": "Below the publication cutoff this run",
}


def _client_status(value: Any) -> str:
    raw = str(value or "").strip()
    return STATUS_LABELS.get(raw, public_lane_name(raw))


def _client_reason(value: Any) -> str:
    raw = str(value or "").strip()
    return REASON_LABELS.get(raw, public_lane_name(raw))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    return _read_json(path) if path.exists() else {}


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def latest_report_token(output_dir: Path) -> str:
    hits: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_indices_review_*.md"):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or "0"), path))
    if not hits:
        raise FileNotFoundError("No weekly_indices_review_*.md file found")
    hits.sort(key=lambda x: (x[0], x[1]))
    return hits[-1][0]


def _latest_plan_path(output_dir: Path) -> Path | None:
    hits: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("index_recommendation_plan_*.json"):
        match = PLAN_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or "0"), path))
    if not hits:
        return None
    hits.sort(key=lambda x: (x[0], x[1]))
    return hits[-1][2]


def _load_plan(output_dir: Path, token: str) -> tuple[dict[str, Any], str]:
    exact = output_dir / f"index_recommendation_plan_{token}.json"
    if exact.exists():
        return _read_json(exact), exact.name
    latest = _latest_plan_path(output_dir)
    if latest and latest.exists():
        return _read_json(latest), latest.name
    return {"recommended_changes": [], "best_new_opportunities": [], "continuity": {}}, "fallback_empty_plan"


def exposure_reason(exposure_id: str, plan: dict[str, Any], fallback: str) -> str:
    for row in plan.get("recommended_changes") or []:
        if row.get("exposure_id") == exposure_id and row.get("reason"):
            return str(row["reason"])
    for row in plan.get("best_new_opportunities") or []:
        if row.get("exposure_id") == exposure_id:
            if row.get("portfolio_gap_fill"):
                return "Improves breadth or fills an important portfolio gap without forcing a low-conviction rotation."
            return "Ranks well enough internally to stay near the live board."
    return fallback


def _read_valuation_history(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _dedupe_valuation_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_date: "OrderedDict[str, dict[str, str]]" = OrderedDict()
    for row in rows:
        key = row.get("requested_close_date") or row.get("as_of") or "unknown"
        by_date[key] = row
    return list(by_date.values())


def public_lane_name(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    if raw in DISPLAY_NAME_OVERRIDES:
        return DISPLAY_NAME_OVERRIDES[raw]
    fallback = raw.replace("_", " ").strip()
    if not fallback:
        return raw
    return fallback[0].upper() + fallback[1:]


def join_public_names(items: Any) -> str:
    if not items:
        return "none"
    if isinstance(items, str):
        items = [items]
    values = [public_lane_name(str(item)) for item in items if str(item).strip()]
    return ", ".join(values) if values else "none"


def _fmt_edge(value: Any) -> str:
    try:
        if value is None:
            return "n/a"
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.2f}%"


def _portfolio_sleeve(row: dict[str, Any]) -> str:
    return str(row.get("portfolio_sleeve") or row.get("public_index_name") or "").strip()


def _benchmark_name(row: dict[str, Any]) -> str:
    return str(row.get("benchmark_name") or row.get("public_index_name") or "").strip()


def _eligibility_note(row: dict[str, Any]) -> str:
    eligibility = row.get("proxy_eligibility") or {}
    note = eligibility.get("note") if isinstance(eligibility, dict) else None
    return str(note or "Proxy eligibility requires current pricing and sufficient history.")


def build_section4(candidate_ranking: dict[str, Any], plan: dict[str, Any]) -> str:
    published = [c for c in candidate_ranking.get("candidates", []) if c.get("publish")]
    published = sorted(published, key=lambda x: (-float(x.get("board_score") or x.get("score") or 0.0), x.get("public_index_name") or ""))[:6]
    summary = candidate_ranking.get("scan_summary") or {}

    lines = [f"## 4. {SECTION4_NAME}", ""]
    if summary:
        lines.append(
            f"The scan covers **{summary.get('coverage_universe_count', 'multiple')} exposures** across **{summary.get('regional_group_count', 'multiple')} regional/style buckets**. The board remains compact by design; broader coverage is shown later in the universe checkpoint."
        )
        lines.append("")
    lines.append("| Portfolio sleeve | Benchmark index | Tradable proxy | Regional / style bucket | Score | Status | Why it is on the board |")
    lines.append("|---|---|---|---|---:|---|---|")
    for row in published:
        status = "Funded" if row.get("currently_held") else "Surfaced"
        fallback_reason = "Ranks high enough internally to remain on the compact published board."
        why = exposure_reason(str(row.get("exposure_id")), plan, fallback_reason)
        lines.append(
            f"| {_portfolio_sleeve(row)} | {_benchmark_name(row)} | {row.get('primary_proxy')} | {row.get('regional_group')} | {float(row.get('board_score') or row.get('score') or 0.0):.2f} | {status} | {why} |"
        )

    close_groups = [g for g in candidate_ranking.get("regional_group_status", []) if g.get("status") == "near_miss"]
    if close_groups:
        strongest = close_groups[0].get("strongest_candidate") or {}
        if strongest:
            lines += [
                "",
                f"The board remains intentionally compact. The strongest omitted regional challenger this run is **{strongest.get('public_index_name')} ({strongest.get('primary_proxy')})**, which remains close enough to matter without displacing a higher-ranked funded exposure.",
            ]
    return "\n".join(lines)


def build_section7(state: dict[str, Any], valuation_rows: list[dict[str, str]]) -> str:
    requested_close = ((state.get("pricing_basis") or {}).get("requested_close_date")) or "unknown"
    total_value = float(state.get("total_portfolio_value_eur") or 0.0)
    starting_capital = float(state.get("starting_capital_eur") or 100000.0)
    ret_pct = ((total_value / starting_capital) - 1.0) * 100.0 if starting_capital else 0.0
    fx_date = ((state.get("pricing_basis") or {}).get("fx_date")) or requested_close
    clean_rows = _dedupe_valuation_rows(valuation_rows)

    lines = [f"## 7. {SECTION7_NAME}", ""]
    lines += [
        f"- Starting capital (EUR): {starting_capital:.2f}",
        f"- Current portfolio value (EUR): {total_value:.2f}",
        f"- Since inception return (%): {ret_pct:.2f}",
        f"- Equity-curve state: {'Inaugural baseline' if len(clean_rows) <= 1 else 'Live tracked'}",
        f"- Pricing basis requested close date: {requested_close}",
        f"- FX reference date: {fx_date}",
        f"- Notes: Holdings and NAV are rebuilt from the pricing/state layer for the requested close date {requested_close}.",
        "",
        "| Date | Portfolio value (EUR) | Comment |",
        "|---|---:|---|",
    ]
    if clean_rows:
        for row in clean_rows[-10:]:
            close_date = row.get("requested_close_date") or row.get("as_of")
            lines.append(
                f"| {close_date} | {float(row.get('total_portfolio_value_eur') or 0.0):.2f} | Pricing basis close {close_date} |"
            )
    else:
        lines.append(f"| {requested_close} | {total_value:.2f} | Live pricing/state rebuild |")
    lines += ["", "`EQUITY_CURVE_CHART_PLACEHOLDER`"]
    return "\n".join(lines)


def build_alternative_duel_table(duels: dict[str, Any]) -> str:
    rows = duels.get("rows", []) or []
    if not rows:
        return "No alternative-duel artifact was available for this run."
    lines = [
        "### Alternative Duel Table",
        "| Current exposure | Current proxy | Alternative / hedge | Alternative proxy | Type | 20d edge | 60d edge | Regime fit | Decision | Required trigger |",
        "|---|---|---|---|---|---:|---:|---|---|---|",
    ]
    for row in rows[:12]:
        duel_type = "Defensive / inverse" if row.get("duel_type") == "defensive_inverse" else "Long alternative"
        lines.append(
            f"| {row.get('current_name')} | {row.get('current_proxy')} | {row.get('alternative_name')} | {row.get('alternative_proxy')} | {duel_type} | {_fmt_edge(row.get('edge_20d_pct'))} | {_fmt_edge(row.get('edge_60d_pct'))} | {row.get('regime_fit')} | {row.get('decision')} | {row.get('required_trigger')} |"
        )
    return "\n".join(lines)


def build_short_radar_table(short_radar: dict[str, Any]) -> str:
    rows = short_radar.get("rows", []) or []
    if not rows:
        return "No defensive / inverse radar artifact was available for this run."
    lines = [
        "### Best Defensive / Inverse Opportunities",
        "These instruments are defensive tools only. They are not part of the base-case long allocation.",
        "",
        "| Candidate | Underlying | Status | Short thesis | Trigger | Invalidation | Max role |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('candidate')} | {row.get('underlying')} | {row.get('client_status')} | {row.get('short_thesis')} | {row.get('trigger')} | {row.get('invalidation')} | {row.get('max_role')} |"
        )
    return "\n".join(lines)


def build_section11(candidate_ranking: dict[str, Any], coverage: dict[str, Any], plan: dict[str, Any], duels: dict[str, Any], short_radar: dict[str, Any]) -> str:
    all_candidates = candidate_ranking.get("candidates", [])
    unpublished = [c for c in all_candidates if not c.get("publish")]
    unpublished = sorted(unpublished, key=lambda x: (-float(x.get("challenger_score") or x.get("score") or 0.0), x.get("public_index_name") or ""))
    coverage_groups = coverage.get("groups") or []
    strongest_omitted = unpublished[0] if unpublished else None
    picked: list[dict[str, Any]] = unpublished[:4]

    lines = [f"## 11. {SECTION11_NAME}", "", "### Long-side Opportunities", ""]
    if strongest_omitted:
        lines.append(
            f"The strongest omitted regional challenger this run is **{strongest_omitted.get('public_index_name')} ({strongest_omitted.get('primary_proxy')})**. It improves breadth and remains close enough to the live board to stay visible in the report."
        )
        lines.append("")

    if picked:
        for idx, row in enumerate(picked, start=1):
            reason = exposure_reason(str(row.get("exposure_id")), plan, "Ranks well internally but remains just below the current publication cutoff.")
            reason_code = _client_reason(row.get("reason_code_if_not_published") or "below_board_cutoff")
            lines += [
                f"#### {idx}. {row.get('public_index_name')} ({row.get('primary_proxy')})",
                f"- Portfolio sleeve: {_portfolio_sleeve(row)}",
                f"- Regional / style bucket: {row.get('regional_group')}",
                f"- Challenger score: {float(row.get('challenger_score') or row.get('score') or 0.0):.2f}",
                f"- Proxy eligibility: {_eligibility_note(row)}",
                f"- Why it matters: {reason}",
                f"- Why not on the board yet: {reason_code}",
                "",
            ]
    else:
        lines += ["No non-published long-side challengers were available for this run.", ""]

    lines += [build_alternative_duel_table(duels), "", build_short_radar_table(short_radar), ""]

    lines += [
        "### Breadth checkpoint by regional bucket",
        "| Regional / style bucket | Strongest candidate | Proxy | Candidate count | Eligible proxies | Challenger score | Current status |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for group in coverage_groups:
        cand = group.get("strongest_candidate") or {}
        if not cand:
            continue
        status = "Published" if cand.get("publish") else _client_status(group.get("status"))
        lines.append(
            f"| {group.get('group')} | {cand.get('public_index_name')} | {cand.get('primary_proxy')} | {int(group.get('candidate_count') or 0)} | {int(group.get('eligible_proxy_count') or 0)} | {float(cand.get('challenger_score') or cand.get('score') or 0.0):.2f} | {status} |"
        )

    lines += [
        "",
        "### Universe scan checkpoint",
        "| Portfolio sleeve | Benchmark index | Regional / style bucket | Tradable proxy | Proxy eligibility | Published? | Challenger score | Why not on the board yet |",
        "|---|---|---|---|---|---|---:|---|",
    ]
    for row in sorted(all_candidates, key=lambda x: (-float(x.get('challenger_score') or x.get('score') or 0.0), x.get('public_index_name') or '')):
        published = "Yes" if row.get("publish") else "No"
        reason_key = "published" if row.get("publish") else (row.get("reason_code_if_not_published") or "below_board_cutoff")
        reason = _client_reason(reason_key)
        lines.append(
            f"| {_portfolio_sleeve(row)} | {_benchmark_name(row)} | {row.get('regional_group')} | {row.get('primary_proxy')} | {_eligibility_note(row)} | {published} | {float(row.get('challenger_score') or row.get('score') or 0.0):.2f} | {reason} |"
        )

    return "\n".join(lines).rstrip()


def build_section15(state: dict[str, Any]) -> str:
    starting_capital = float(state.get("starting_capital_eur") or 100000.0)
    total_value = float(state.get("total_portfolio_value_eur") or 0.0)
    cash_eur = float(state.get("cash_eur") or 0.0)
    invested_eur = total_value - cash_eur
    ret_pct = ((total_value / starting_capital) - 1.0) * 100.0 if starting_capital else 0.0
    requested_close = ((state.get("pricing_basis") or {}).get("requested_close_date")) or "unknown"
    fx_date = ((state.get("pricing_basis") or {}).get("fx_date")) or requested_close

    lines = [f"## 15. {SECTION15_NAME}", ""]
    lines += [
        f"- Starting capital (EUR): {starting_capital:.2f}",
        f"- Invested market value (EUR): {invested_eur:.2f}",
        f"- Cash (EUR): {cash_eur:.2f}",
        f"- Total portfolio value (EUR): {total_value:.2f}",
        f"- Since inception return (%): {ret_pct:.2f}",
        f"- Pricing basis requested close date: {requested_close}",
        f"- FX reference date: {fx_date}",
        "",
        "| Ticker | Public index / exposure | Shares | Price (local) | Currency | Market value (local) | Market value (EUR) | Weight % |",
        "|---|---|---:|---:|---|---:|---:|---:|",
    ]
    for pos in state.get("positions") or []:
        lines.append(
            f"| {pos.get('primary_proxy')} | {pos.get('display_name')} | {int(pos.get('shares') or 0)} | {float(pos.get('latest_proxy_close') or 0.0):.2f} | {pos.get('proxy_currency') or 'USD'} | {float(pos.get('market_value_local') or 0.0):.2f} | {float(pos.get('market_value_eur') or 0.0):.2f} | {float(pos.get('weight_pct') or 0.0):.2f} |"
        )
    lines.append(f"| CASH | Residual cash | - | 1.00 | EUR | {cash_eur:.2f} | {cash_eur:.2f} | {(cash_eur / total_value * 100.0 if total_value else 0.0):.2f} |")
    return "\n".join(lines)


def build_section16(candidate_ranking: dict[str, Any], coverage: dict[str, Any], plan: dict[str, Any]) -> str:
    continuity = plan.get("continuity") or {}
    lines = [f"## 16. {SECTION16_NAME}", ""]
    lines += [
        "### Watchlist / dynamic radar memory",
        "| Theme | Regional / style bucket | Primary proxy | Status | Why it stays visible |",
        "|---|---|---|---|---|",
    ]
    watch_candidates = sorted(
        [c for c in candidate_ranking.get("candidates", []) if not c.get("publish")],
        key=lambda x: (-float(x.get("challenger_score") or x.get("score") or 0.0), x.get("public_index_name") or ""),
    )[:10]
    for row in watch_candidates:
        status = "Strong challenger" if row.get("reason_code_if_not_published") == "strong_challenger_not_published" else "Watchlist"
        why = exposure_reason(str(row.get("exposure_id")), plan, "Broad discovery keeps it visible even though it did not make the compact board.")
        lines.append(
            f"| {row.get('public_index_name')} | {row.get('regional_group')} | {row.get('primary_proxy')} | {status} | {why} |"
        )

    lines += [
        "",
        "### Discovery coverage checkpoint",
        "| Regional / style bucket | Status | Candidates scanned | Eligible proxies | Strongest candidate | Proxy | Score |",
        "|---|---|---:|---:|---|---|---:|",
    ]
    for group in coverage.get("groups") or []:
        cand = group.get("strongest_candidate") or {}
        lines.append(
            f"| {group.get('group')} | {_client_status(group.get('status'))} | {int(group.get('candidate_count') or 0)} | {int(group.get('eligible_proxy_count') or 0)} | {cand.get('public_index_name', '—')} | {cand.get('primary_proxy', '—')} | {float(cand.get('challenger_score') or cand.get('score') or 0.0):.2f} |"
        )

    lines += [
        "",
        "### Lane continuity notes",
        f"- Retained entries: {join_public_names(continuity.get('retained_entries'))}",
        f"- New entries: {join_public_names(continuity.get('new_entries'))}",
        f"- Dropped entries: {join_public_names(continuity.get('dropped_entries'))}",
        f"- Strong challengers not published: {join_public_names(continuity.get('strong_challengers_not_published'))}",
        f"- What would most likely change the board next run: {continuity.get('next_change_trigger') or 'No trigger recorded.'}",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output_indices")
    parser.add_argument("--token", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    token = args.token or latest_report_token(output_dir)

    ranking_path = output_dir / f"index_candidate_ranking_{token}.json"
    coverage_path = output_dir / f"index_discovery_coverage_{token}.json"
    state_path = output_dir / "index_portfolio_state.json"
    valuation_path = output_dir / "index_valuation_history.csv"
    duel_path = output_dir / "research" / f"index_alternative_duels_{token}.json"
    short_radar_path = output_dir / "research" / f"index_short_radar_{token}.json"

    if not ranking_path.exists():
        raise FileNotFoundError(f"Missing ranking artifact: {ranking_path}")
    if not coverage_path.exists():
        raise FileNotFoundError(f"Missing discovery coverage artifact: {coverage_path}")
    if not state_path.exists():
        raise FileNotFoundError(f"Missing portfolio state artifact: {state_path}")

    candidate_ranking = _read_json(ranking_path)
    coverage = _read_json(coverage_path)
    plan, plan_source = _load_plan(output_dir, token)
    state = _read_json(state_path)
    valuation_rows = _read_valuation_history(valuation_path)
    duels = _read_json_if_exists(duel_path)
    short_radar = _read_json_if_exists(short_radar_path)

    assembled_dir = output_dir / "assembled"
    sec4 = build_section4(candidate_ranking, plan)
    sec7 = build_section7(state, valuation_rows)
    sec11 = build_section11(candidate_ranking, coverage, plan, duels, short_radar)
    sec15 = build_section15(state)
    sec16 = build_section16(candidate_ranking, coverage, plan)

    section4_path = assembled_dir / f"section4_index_opportunity_board_{token}.md"
    section7_path = assembled_dir / f"section7_equity_curve_{token}.md"
    section11_path = assembled_dir / f"section11_best_new_index_opportunities_{token}.md"
    section15_path = assembled_dir / f"section15_holdings_and_cash_{token}.md"
    section16_path = assembled_dir / f"section16_continuity_input_{token}.md"
    combined_path = assembled_dir / f"weekly_indices_artifact_blocks_{token}.md"

    _write_text(section4_path, sec4)
    _write_text(section7_path, sec7)
    _write_text(section11_path, sec11)
    _write_text(section15_path, sec15)
    _write_text(section16_path, sec16)
    _write_text(combined_path, "\n\n".join([sec4, sec7, sec11, sec15, sec16]))

    print(
        f"ASSEMBLY_BLOCKS_OK | token={token} | plan_source={plan_source} | section4={section4_path.name} | section7={section7_path.name} | "
        f"section11={section11_path.name} | section15={section15_path.name} | section16={section16_path.name} | combined={combined_path.name}"
    )


if __name__ == "__main__":
    main()
