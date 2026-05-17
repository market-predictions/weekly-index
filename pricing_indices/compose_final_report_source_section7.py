from __future__ import annotations

from pricing_indices import compose_final_report as _base


def _no_section15_performance_append(output_dir):
    """Disable legacy Section 15 performance-table append.

    The tradable proxy performance table is now produced at source in Section 7
    by pricing_indices.assemble_report_sections_source_section7. Section 15 must
    remain holdings/cash only.
    """
    return ""


_base.build_tradable_proxy_performance_table = _no_section15_performance_append


def main() -> None:
    _base.main()


if __name__ == "__main__":
    main()
