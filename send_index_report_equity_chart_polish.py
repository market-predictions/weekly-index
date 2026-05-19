from __future__ import annotations

from datetime import datetime
from pathlib import Path

import send_index_report as _base

_ORIG_CREATE_EQUITY_CURVE_PNG = _base.create_equity_curve_png


def create_equity_curve_png(output_dir: Path, chart_path: Path, md_text: str | None = None) -> Path | None:
    """Render the equity curve with print-safe date labels.

    The base renderer allowed Matplotlib to choose a dense date axis. As the
    valuation history grew, late-April / early-May labels started to overlap in
    the PDF. This override keeps the chart compact while capping visible date
    ticks and using short rotated labels.
    """
    if _base.plt is None:
        return None

    try:
        import matplotlib.dates as mdates
    except Exception:  # noqa: BLE001
        return _ORIG_CREATE_EQUITY_CURVE_PNG(output_dir, chart_path, md_text=md_text)

    points: list[tuple[str, float]] = []
    if md_text:
        points = _base.parse_section7_equity_points(md_text)
    if not points:
        for report_path in _base.latest_reports_by_day(output_dir):
            hist_md = report_path.read_text(encoding="utf-8")
            report_date = _base.parse_report_date(hist_md)
            totals = _base.parse_section15_totals(hist_md)
            nav = totals.get("Total portfolio value (EUR)")
            if nav is not None:
                points.append((report_date, nav))
    if not points:
        return None

    dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in points]
    values = [v for _, v in points]

    fig, ax = _base.plt.subplots(figsize=(9.2, 3.9))
    ax.plot(dates, values, marker="o", linewidth=2.2)
    ax.set_title("Equity Curve (EUR)", pad=10)
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio value (EUR)")
    ax.grid(True, alpha=0.28)

    locator = mdates.AutoDateLocator(minticks=4, maxticks=6)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.tick_params(axis="x", labelsize=8, pad=5)
    ax.tick_params(axis="y", labelsize=8)
    for label in ax.get_xticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment("right")

    fig.tight_layout(pad=1.15)
    fig.subplots_adjust(bottom=0.24)
    fig.savefig(chart_path, dpi=180)
    _base.plt.close(fig)
    return chart_path


_base.create_equity_curve_png = create_equity_curve_png
