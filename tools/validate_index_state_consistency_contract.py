from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path("output_indices")
REPORT_RE = re.compile(r"weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")


def _latest_report() -> Path:
    hits: list[tuple[str, int, Path]] = []
    for path in OUTPUT_DIR.glob("weekly_indices_review_*.md"):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or "1"), path))
    if not hits:
        raise RuntimeError("State consistency contract failed: no weekly_indices_review_*.md report found.")
    hits.sort(key=lambda item: (item[0], item[1]))
    return hits[-1][2]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _amount_variants(value: Any) -> set[str]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return set()
    return {
        f"{number:.2f}",
        f"{number:,.2f}",
        f"{number:.0f}",
        f"{number:,.0f}",
    }


def _find_amounts(text: str) -> set[str]:
    return set(re.findall(r"\b\d{1,3}(?:,\d{3})+(?:\.\d{2})\b|\b\d{5,6}\.\d{2}\b", text))


def _known_state_values(state: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    values |= _amount_variants(state.get("total_portfolio_value_eur"))
    values |= _amount_variants(state.get("cash_eur"))
    for position in state.get("positions", []) or []:
        values |= _amount_variants(position.get("market_value_eur"))
        values |= _amount_variants(position.get("market_value_local"))
        values |= _amount_variants(position.get("latest_proxy_close"))
        performance = position.get("performance") or {}
        values |= _amount_variants(performance.get("pnl_eur"))
    return {v for v in values if v}


def _report_date_from_name(path: Path) -> str | None:
    match = REPORT_RE.match(path.name)
    if not match:
        return None
    token = match.group(1)
    return f"20{token[:2]}-{token[2:4]}-{token[4:6]}"


def _allowed_early_dates(report_path: Path, requested_close: str) -> set[str]:
    allowed = {requested_close} if requested_close else set()
    report_date = _report_date_from_name(report_path)
    if report_date:
        allowed.add(report_date)
    return allowed


def validate() -> None:
    report_path = _latest_report()
    state_path = OUTPUT_DIR / "index_portfolio_state.json"
    if not state_path.exists():
        raise RuntimeError("State consistency contract failed: missing output_indices/index_portfolio_state.json")
    state = _read_json(state_path)
    text = report_path.read_text(encoding="utf-8")

    requested_close = str((state.get("pricing_basis") or {}).get("requested_close_date") or "").strip()
    total_value = state.get("total_portfolio_value_eur")
    cash = state.get("cash_eur")

    if requested_close and requested_close not in text:
        raise RuntimeError(f"State consistency contract failed: requested close {requested_close} not visible in report {report_path.name}.")
    if total_value is not None and not any(v in text for v in _amount_variants(total_value)):
        raise RuntimeError(f"State consistency contract failed: total NAV {total_value} not visible in report {report_path.name}.")
    if cash is not None and not any(v in text for v in _amount_variants(cash)):
        raise RuntimeError(f"State consistency contract failed: cash {cash} not visible in report {report_path.name}.")

    positions = state.get("positions") or []
    if positions:
        if "Tradable Proxy Performance" not in text:
            raise RuntimeError("State consistency contract failed: missing Tradable Proxy Performance table.")
        if "1w return" not in text or "Since-entry" not in text or "Contribution %" not in text:
            raise RuntimeError("State consistency contract failed: Tradable Proxy Performance table is missing required columns.")
        missing_perf = []
        for position in positions:
            proxy = str(position.get("primary_proxy") or "").strip()
            performance = position.get("performance") or {}
            if proxy and proxy not in text:
                missing_perf.append(f"{proxy}:not_visible")
            for field in ["one_week_return_pct", "one_month_return_pct", "three_month_return_pct", "since_entry_return_pct", "contribution_pct"]:
                if field not in performance:
                    missing_perf.append(f"{proxy or position.get('exposure_id')}:{field}")
        if missing_perf:
            raise RuntimeError("State consistency contract failed: performance state/report mismatch: " + ", ".join(missing_perf))

    early_text = "\n".join(text.splitlines()[:80])
    allowed_dates = _allowed_early_dates(report_path, requested_close)
    stale_early_dates = sorted(set(re.findall(r"2026-\d{2}-\d{2}", early_text)) - allowed_dates)
    if stale_early_dates:
        raise RuntimeError(
            f"State consistency contract failed: stale pricing dates appear in executive/action sections: {', '.join(stale_early_dates)}"
        )

    known = _known_state_values(state)
    suspicious_amounts = []
    early_amounts = _find_amounts(early_text)
    for amount in early_amounts:
        if amount not in known and amount not in {"100000.00", "100,000.00"}:
            suspicious_amounts.append(amount)
    if suspicious_amounts:
        raise RuntimeError(
            "State consistency contract failed: possible stale EUR amounts in executive/action sections: "
            + ", ".join(sorted(suspicious_amounts))
        )

    print(
        f"INDEX_STATE_CONSISTENCY_OK | report={report_path.name} | requested_close={requested_close} | total_nav={total_value} | cash={cash} | performance_rows={len(positions)}"
    )


if __name__ == "__main__":
    validate()
