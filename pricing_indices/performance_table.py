from __future__ import annotations

from typing import Any


def _fmt_pct(value: Any) -> str:
    try:
        if value is None:
            return "n/a"
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.2f}%"


def _fmt_eur(value: Any) -> str:
    try:
        if value is None:
            return "n/a"
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "n/a"


def build_tradable_proxy_performance_table(state: dict[str, Any]) -> str:
    """Render the ETF-style tradable proxy performance table.

    This belongs in Section 7 because it explains portfolio development directly
    after the equity curve. Section 15 remains limited to current holdings and
    cash state.
    """
    positions = state.get("positions") or []
    if not positions:
        return ""

    lines = [
        "### Tradable Proxy Performance",
        "Performance is calculated on the tradable ETF proxies used for portfolio valuation. Benchmark index prices remain the analysis reference; tradable proxy closes drive market value, P/L and contribution.",
        "",
        "| Portfolio sleeve | Benchmark index | Tradable proxy | Weight % | 1w return | 1m return | 3m return | Since-entry | P/L EUR | Contribution % |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for pos in positions:
        perf = pos.get("performance") or {}
        sleeve = pos.get("portfolio_sleeve") or pos.get("display_name") or pos.get("exposure_id")
        benchmark = pos.get("benchmark_name") or pos.get("display_name") or pos.get("benchmark_symbol")
        lines.append(
            f"| {sleeve} | {benchmark} | {pos.get('primary_proxy')} | {float(pos.get('weight_pct') or 0.0):.2f} | "
            f"{_fmt_pct(perf.get('one_week_return_pct'))} | {_fmt_pct(perf.get('one_month_return_pct'))} | "
            f"{_fmt_pct(perf.get('three_month_return_pct'))} | {_fmt_pct(perf.get('since_entry_return_pct'))} | "
            f"{_fmt_eur(perf.get('pnl_eur'))} | {_fmt_pct(perf.get('contribution_pct'))} |"
        )

    return "\n".join(lines)
