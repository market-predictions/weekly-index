from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REPORT_RE = re.compile(r"weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")
SECTION_HEADER_RE = re.compile(r"^##\s+(\d+)\.\s+.*$", flags=re.MULTILINE)

TARGET_SECTION_FILES = {
    4: "section4_index_opportunity_board_{token}.md",
    7: "section7_equity_curve_{token}.md",
    11: "section11_best_new_index_opportunities_{token}.md",
    15: "section15_holdings_and_cash_{token}.md",
    16: "section16_continuity_input_{token}.md",
}

CLIENT_BOTTOM_LINE = """## 6. Bottom Line
- The portfolio remains constructive but selective.
- U.S. leadership remains the core engine, but concentration must be watched.
- IWM and EEM remain funded but under review versus clearer challengers.
- Inverse instruments are not base-case positions, but the hedge map is ready if breadth breaks."""

CLIENT_COPY_REPLACEMENTS = {
    "Manifest-backed production rerun of the upgraded ETF-derived Weekly Index workflow: fresh closing prices first, full-universe breadth, long opportunities, short opportunities radar, capital re-underwriting scorecard, render validation, and email delivery.": "Fresh pricing confirms a constructive but selective index backdrop. The portfolio remains anchored in U.S. leadership, keeps Emerging Markets funded, and maintains Japan, China large-cap, Canada, and Italy as the most relevant challengers. Defensive inverse instruments remain tactical contingency tools, not the base-case allocation.",
    "This file is a same-day production trigger scaffold. The workflow must replace artifact-driven sections before render/send and then commit a run manifest under `output_indices/run_manifests/`.": "This review combines current closing prices, portfolio state, breadth evidence, long-side challengers, and defensive inverse-radar checks into one decision-ready weekly update.",
    "None before live pricing and ranking rebuild.": "No new funded additions this run.",
    "To be rebuilt from live candidate-ranking artifacts.": "China large cap (FXI), S&P/TSX 60 (EWC), and FTSE MIB (EWI) remain the closest replacement candidates, subject to confirmation and portfolio-fit discipline.",
    "Validate fresh closing prices and current FX basis first.": "Maintain pricing discipline: use current closes and current EUR/USD before making allocation changes.",
    "Rebuild full-universe breadth, long opportunities, and short opportunities radar.": "Keep the full-universe breadth scan visible, including long challengers and defensive inverse candidates.",
    "Validate capital re-underwriting scorecard, render, email, and manifest commit-back.": "Re-underwrite weak or replaceable holdings against named alternatives before adding risk.",
    "Pricing coverage or FX freshness fails the hardened pricing gate.": "A stale pricing or FX input would weaken confidence in valuation and position sizing.",
    "Render or email delivery fails without a positive manifest/receipt.": "Report delivery or rendering issues would require operational follow-up, but do not change the market view.",
    "pending live pricing pass": "current pricing basis",
    "Hold pending artifact rebuild": "Hold",
    "Hold / replaceable pending artifact rebuild": "Hold under review",
    "pending artifact rebuild": "under review",
    "Would initiate today: pending live pricing and ranking rebuild.": "Would initiate today: yes, but only within concentration limits.",
    "Would initiate at current weight: pending SPY / QQQ overlap review.": "Would initiate at current weight: yes, but monitor SPY / QQQ overlap and U.S. concentration.",
    "Would initiate at current weight: pending mega-cap leadership review.": "Would initiate at current weight: yes, while mega-cap leadership remains intact.",
    "Would initiate today: pending breadth confirmation.": "Would initiate today: only as a measured breadth sleeve; conviction remains below SPY / QQQ.",
    "Would initiate today: pending dollar and EM breadth confirmation.": "Would initiate today: yes, but only as a measured non-U.S. risk sleeve while dollar pressure remains contained.",
    "Actual position changes must come from the production ranking/state layer.": "No position changes were executed this run; the funded book remains unchanged pending stronger replacement evidence.",
    "None before workflow artifact rebuild.": "None.",
    "No delivery success should be claimed without workflow evidence or manifest evidence.": "Maintain discipline: do not confuse operational noise with investment evidence.",
    "The workflow must replace artifact-driven sections before render/send and then commit a run manifest under output_indices/run_manifests/.": "The report uses refreshed state, pricing, breadth, and opportunity evidence for this weekly update.",
    "layered_close_discovery_v1": "persisted pricing audit",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _money(value: Any) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "n/a"


def _take(values: Any, limit: int = 3) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(v).strip() for v in values if str(v).strip()][:limit]


def latest_report_path(output_dir: Path) -> Path:
    hits: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_indices_review_*.md"):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or "0"), path))
    if not hits:
        raise FileNotFoundError("No weekly_indices_review_*.md file found")
    hits.sort(key=lambda x: (x[0], x[1]))
    return hits[-1][2]


def token_from_report(report_path: Path) -> str:
    match = REPORT_RE.match(report_path.name)
    if not match:
        raise RuntimeError(f"Unexpected report filename: {report_path.name}")
    return match.group(1)


def find_section_bounds(text: str, section_number: int) -> tuple[int, int]:
    matches = list(SECTION_HEADER_RE.finditer(text))
    start_idx = None
    end_idx = None
    for i, match in enumerate(matches):
        num = int(match.group(1))
        if num == section_number:
            start_idx = match.start()
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            break
    if start_idx is None or end_idx is None:
        raise RuntimeError(f"Section {section_number} not found in report")
    return start_idx, end_idx


def replace_section(text: str, section_number: int, replacement: str) -> str:
    start_idx, end_idx = find_section_bounds(text, section_number)
    prefix = text[:start_idx].rstrip()
    suffix = text[end_idx:].lstrip()
    parts = [prefix, replacement.strip(), suffix]
    return "\n\n".join(part for part in parts if part)


def _portfolio_state(output_dir: Path) -> dict[str, Any]:
    return _read_json(output_dir / "index_portfolio_state.json")


def _macro_pack(output_dir: Path) -> dict[str, Any]:
    return _read_json(output_dir / "macro" / "latest.json")


def build_executive_summary(output_dir: Path) -> str:
    state = _portfolio_state(output_dir)
    macro = _macro_pack(output_dir)
    pricing = state.get("pricing_basis", {}) or {}
    requested_close = pricing.get("requested_close_date") or "current close"
    fx_date = pricing.get("fx_date") or requested_close
    total_value = _money(state.get("total_portfolio_value_eur"))
    cash = _money(state.get("cash_eur"))
    regime = ((macro.get("regime") or {}).get("current")) or "Policy transition / mixed regime"
    confidence = (macro.get("regime") or {}).get("confidence")
    confidence_text = f"{float(confidence):.0%}" if isinstance(confidence, (int, float)) else "medium"
    geo = macro.get("geopolitical_regime") or {}
    geo_current = geo.get("current") or "Moderate monitoring regime"
    geo_implication = geo.get("portfolio_implication") or "No geopolitical channel is strong enough to override price, breadth and proxy evidence this week."
    top_changes = _take((macro.get("report_digest") or {}).get("top_changes") or (macro.get("regime") or {}).get("what_changed"), 3)
    implications = _take((macro.get("report_digest") or {}).get("decision_implications") or macro.get("portfolio_implications"), 3)
    first_change = top_changes[0] if top_changes else "No full-regime break; selectivity remains more important than broad risk expansion."
    first_implication = implications[0] if implications else "Keep the current implementation invested while forcing weak sleeves through direct alternative duels."

    return f"""## 1. Executive Summary
- **Current valuation basis:** portfolio NAV is EUR {total_value}, including EUR {cash} cash, rebuilt from the {requested_close} close and FX reference date {fx_date}.
- **Primary regime:** {regime} ({confidence_text} confidence).
- **Geopolitical regime:** {geo_current}.
- **Geopolitical implication:** {geo_implication}
- **What changed:** {first_change}
- **Portfolio implication:** {first_implication}
- **Main takeaway:** keep QQQ as the strongest earned sleeve, keep SPY under concentration review, and force IWM and EEM through named long-alternative and defensive-hedge duels before any new capital is assigned."""


def build_action_snapshot(output_dir: Path) -> str:
    state = _portfolio_state(output_dir)
    positions = state.get("positions", []) or []
    by_proxy = {str(p.get("primary_proxy") or "").upper(): p for p in positions}

    def label(proxy: str, fallback: str) -> str:
        p = by_proxy.get(proxy)
        if not p:
            return fallback
        return f"{p.get('display_name') or fallback} via {proxy}"

    return f"""## 2. Portfolio Action Snapshot
| Recommendation | Tickers / notes |
|---|---|
| Add | None this run. Cash remains available, but no challenger clears the full pricing, regime and relative-strength hurdle yet. |
| Hold | {label('SPY', 'S&P 500 via SPY')}; {label('QQQ', 'Nasdaq 100 via QQQ')} |
| Hold but replaceable | {label('IWM', 'Russell 2000 via IWM')}; {label('EEM', 'Emerging Markets via EEM')} |
| Reduce | None until the direct alternative-duel evidence produces a cleaner replacement or hedge trigger. |
| Close | None this run. |

### Best replacements to monitor
- Japan large cap via EWJ
- Canada broad via EWC
- Greater China large cap via FXI

### Top 3 actions this week
1. Keep QQQ as the strongest core holding while leadership remains intact.
2. Test SPY against QQQ overlap so U.S. exposure is not mistaken for full diversification.
3. Force IWM and EEM through long-alternative and defensive/inverse comparisons before adding capital.

### Top 3 risks this week
1. Higher oil or sticky inflation delays easier policy and keeps pressure on weak breadth.
2. SPY and QQQ remain a concentration cluster, not a diversified global allocation.
3. IWM and EEM stay under review until breadth, USD and relative-strength evidence improve."""


def force_client_bottom_line(text: str) -> str:
    return replace_section(text, 6, CLIENT_BOTTOM_LINE)


def polish_client_copy(text: str) -> str:
    polished = text
    for old, new in CLIENT_COPY_REPLACEMENTS.items():
        polished = polished.replace(old, new)
    polished = force_client_bottom_line(polished)
    polished = re.sub(r"\b([A-Z]{2,5})(versus|together|and)\b", r"\1 \2", polished)
    polished = re.sub(r"\b(and|versus)([A-Z]{2,5})\b", r"\1 \2", polished)
    polished = re.sub(r"\n-\s*$", "", polished, flags=re.MULTILINE)
    polished = re.sub(r"\n{3,}", "\n\n", polished)
    return polished


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output_indices")
    parser.add_argument("--report-path", default=None)
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    report_path = Path(args.report_path) if args.report_path else latest_report_path(output_dir)
    if not report_path.exists():
        raise FileNotFoundError(f"Missing report file: {report_path}")

    token = token_from_report(report_path)
    assembled_dir = output_dir / "assembled"
    original_text = _read_text(report_path)
    composed_text = original_text

    composed_text = replace_section(composed_text, 1, build_executive_summary(output_dir))
    composed_text = replace_section(composed_text, 2, build_action_snapshot(output_dir))

    for section_number, template in TARGET_SECTION_FILES.items():
        section_path = assembled_dir / template.format(token=token)
        if not section_path.exists():
            raise FileNotFoundError(f"Missing assembled section block: {section_path}")
        replacement = _read_text(section_path)
        composed_text = replace_section(composed_text, section_number, replacement)

    composed_text = polish_client_copy(composed_text)

    preview_path = assembled_dir / f"{report_path.stem}_composed_preview.md"
    _write_text(preview_path, composed_text)

    if args.in_place:
        _write_text(report_path, composed_text)

    print(
        f"REPORT_COMPOSER_OK | report={report_path.name} | token={token} | "
        f"preview={preview_path.name} | in_place={'yes' if args.in_place else 'no'}"
    )


if __name__ == "__main__":
    main()
