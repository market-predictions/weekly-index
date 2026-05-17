from __future__ import annotations

from typing import Any

from pricing_indices import assemble_report_sections as _base
from pricing_indices.performance_table import build_tradable_proxy_performance_table

_ORIG_BUILD_SECTION7 = _base.build_section7


def build_section7(state: dict[str, Any], valuation_rows: list[dict[str, str]]) -> str:
    """Build Section 7 with performance table at source assembly time.

    This replaces the older post-composition relocation workaround. The equity
    curve and tradable proxy performance table now share the same portfolio
    development section before the report is composed.
    """
    section = _ORIG_BUILD_SECTION7(state, valuation_rows).rstrip()
    performance_table = build_tradable_proxy_performance_table(state).strip()
    if not performance_table:
        return section
    if "### Tradable Proxy Performance" in section:
        return section
    return section + "\n\n" + performance_table


_base.build_section7 = build_section7


def main() -> None:
    _base.main()


if __name__ == "__main__":
    main()
