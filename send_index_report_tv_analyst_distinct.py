from __future__ import annotations

import send_index_report as _base
import send_index_report_tv  # noqa: F401 - applies TradingView/ticker rendering patches

_ORIG_BUILD_REPORT_HTML = _base.build_report_html

ANALYST_DISTINCTION_CSS = """
    .analyst-hero {
      background: #2F4A66 !important;
      color: #FFFFFF !important;
      margin-top: 30px;
      page-break-before: always;
      break-before: page;
    }
    .analyst-hero .masthead,
    .analyst-hero .hero-sub,
    .analyst-hero .hero-side-label {
      color: #FFFFFF !important;
    }
    .analyst-part-label {
      display: inline-block;
      margin: 0 0 8px 0;
      padding: 4px 9px;
      border: 1px solid rgba(255,255,255,0.45);
      border-radius: 999px;
      color: #FFFFFF;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: .12em;
      text-transform: uppercase;
    }
    .analyst-subtitle {
      margin-top: 7px;
      color: #E8EEF3;
      font-size: 12px;
      font-weight: 500;
      letter-spacing: .02em;
      white-space: normal;
    }
    .analyst-hero + .hero-rule {
      background: #C9A96A !important;
      height: 6px;
    }
    .analyst-hero ~ .panel {
      background: #F4F6F8;
      border-color: #CBD3DB;
    }
    .analyst-hero ~ .panel .section-badge {
      background: #2F4A66;
      color: #FFFFFF;
    }
    .analyst-hero ~ .panel .section-label {
      color: #2F4A66;
    }
    .analyst-hero ~ .panel th {
      background: #E8EDF2;
    }
    @media print {
      .analyst-hero {
        page-break-before: always;
        break-before: page;
      }
    }
"""


def _inject_css(html: str) -> str:
    if "analyst-hero" in html and "#2F4A66" in html:
        return html
    return html.replace("</style>", ANALYST_DISTINCTION_CSS + "\n        </style>", 1)


def _mark_analyst_hero(html: str) -> str:
    html = html.replace("<div class='hero hero-secondary'>", "<div class='hero hero-secondary analyst-hero'>", 1)
    html = html.replace(
        "<td class='hero-right'><div class='hero-side-label'>Analyst Report</div></td>",
        "<td class='hero-right'><div class='analyst-part-label'>PART II</div><div class='hero-side-label'>Analyst Report</div><div class='analyst-subtitle'>Research depth, scenario framing and implementation detail</div></td>",
        1,
    )
    return html


def build_report_html(md_text: str, report_date_str: str, image_src: str | None = None, render_mode: str = "email") -> str:
    html = _ORIG_BUILD_REPORT_HTML(md_text, report_date_str, image_src=image_src, render_mode=render_mode)
    html = _mark_analyst_hero(html)
    html = _inject_css(html)
    return html


_base.build_report_html = build_report_html


def main() -> None:
    _base.main()


if __name__ == "__main__":
    main()
