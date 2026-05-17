from __future__ import annotations

import re

import send_index_report as _base
import send_index_report_tv  # noqa: F401 - applies TradingView/ticker rendering patches

_ORIG_BUILD_REPORT_HTML = _base.build_report_html

ANALYST_DISTINCTION_CSS = """
    .analyst-hero {
      background: #0F5B5C !important;
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
      color: #E8F3F2;
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
      background: #F5F8F8;
      border-color: #CCD9D9;
    }
    .analyst-hero ~ .panel .section-badge {
      background: #0F5B5C;
      color: #FFFFFF;
    }
    .analyst-hero ~ .panel .section-label {
      color: #0B4446;
    }
    .analyst-hero ~ .panel th {
      background: #E4EEEE;
    }
    .analyst-hero ~ .panel .position-card,
    .analyst-hero ~ .panel .subblock,
    .analyst-hero ~ .panel .chart-wrap {
      background: #FFFFFF;
      border-color: #D6E1E1;
    }
    .analyst-hero ~ .panel .position-card-title,
    .analyst-hero ~ .panel .subblock-title,
    .analyst-hero ~ .panel h3 {
      color: #0B4446;
    }
    .analyst-hero ~ .panel tr:nth-child(even) td {
      background: #F7FBFB;
    }
    .inline-list {
      margin: 0 0 12px 0;
      padding: 0;
    }
    .inline-list-item {
      display: block;
      margin: 0 0 5px 0;
      padding: 0;
      font-size: 14px;
      line-height: 1.58;
      font-weight: 400;
    }
    .inline-list-marker {
      font-weight: 400;
      margin-right: 4px;
    }
    @media print {
      .analyst-hero {
        page-break-before: always;
        break-before: page;
      }
    }
"""

LI_RE = re.compile(r"<li>(.*?)</li>", re.DOTALL | re.IGNORECASE)
UL_RE = re.compile(r"<ul>(.*?)</ul>", re.DOTALL | re.IGNORECASE)
OL_RE = re.compile(r"<ol>(.*?)</ol>", re.DOTALL | re.IGNORECASE)


def _clean_li_inner(inner: str) -> str:
    inner = inner.strip()
    if inner.startswith("<p>") and inner.endswith("</p>"):
        inner = inner[3:-4].strip()
    return inner


def _convert_list_block(content: str, ordered: bool) -> str:
    items = LI_RE.findall(content)
    if not items:
        return content
    rows = []
    for idx, item in enumerate(items, start=1):
        marker = f"{idx}." if ordered else "•"
        rows.append(
            "<div class='inline-list-item'>"
            f"<span class='inline-list-marker'>{marker}</span>"
            f"{_clean_li_inner(item)}"
            "</div>"
        )
    return "<div class='inline-list'>" + "".join(rows) + "</div>"


def _inline_native_lists(html: str) -> str:
    previous = None
    current = html
    while previous != current:
        previous = current
        current = UL_RE.sub(lambda m: _convert_list_block(m.group(1), ordered=False), current)
        current = OL_RE.sub(lambda m: _convert_list_block(m.group(1), ordered=True), current)
    return current


def _inject_css(html: str) -> str:
    if "analyst-hero" in html and "#0F5B5C" in html and "inline-list-item" in html:
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
    html = _inline_native_lists(html)
    html = _inject_css(html)
    return html


_base.build_report_html = build_report_html


def main() -> None:
    _base.main()


if __name__ == "__main__":
    main()
