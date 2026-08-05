#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import send_index_report as _base
import send_index_report_tv_analyst_distinct  # noqa: F401

NL_REPORT_RE = re.compile(r"^weekly_indices_review_nl_(\d{6})(?:_(\d{2}))?\.md$")
NL_LONG_DATE_RE = re.compile(
    r"\b(?:maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)\s+\d{1,2}\s+"
    r"(?:januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\s+20\d{2}\b",
    re.I,
)
HTML_TAG_RE = re.compile(r"(<[^>]+>)")
HTML_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9.\-]{1,11})(?![A-Za-z0-9])")
MARKDOWN_TV_LINK_LITERAL_RE = re.compile(r"\[([A-Z][A-Z0-9.\-]{1,11})\]\(https://www\.tradingview\.com/chart/\?symbol=[^)]+\)")
HTML_LINKABLE_TICKERS = {
    'SPY', 'QQQ', 'IWM', 'EEM', 'EWJ', 'EWC', 'FXI', 'EWT', 'VLUE', 'EWY', 'QUAL', 'RSP',
    'EWI', 'EWN', 'EWU', 'EWL', 'EWA', 'INDA', 'EWW', 'EWZ', 'EZA', 'EIDO', 'KSA', 'EWP',
    'EWG', 'FEZ', 'EWH', 'EWQ', 'RWM', 'PSQ', 'EUM', 'USMV', 'QQQM', 'VOO', 'VWO', 'VTWO',
    'DXJ', 'IEUR', 'SH', 'EFZ',
}

NL_REQUIRED_HEADINGS = [
    "# Weekly Index Review",
    "## 1. Samenvatting",
    "## 2. Portefeuille-acties in één oogopslag",
    "## 3. Wereldwijd regimedashboard",
    "## 4. Indexkansenbord",
    "## 5. Belangrijkste risico’s / ontkrachters",
    "## 6. Kernconclusie",
    "## 7. Vermogenscurve en portefeuilleontwikkeling",
    "## 8. Regionale en stijlallocatiekaart",
    "## 9. Tweede-orde-effectenkaart",
    "## 10. Beoordeling huidige posities",
    "## 11. Beste nieuwe indexkansen",
    "## 12. Portefeuillerotatieplan",
    "## 13. Definitieve actietabel",
    "## 14. Positiewijzigingen in deze run",
    "## 15. Huidige portefeuilleposities en cash",
    "## 16. Continuïteitsinvoer voor de volgende run",
    "## 17. Disclaimer",
]

NL_DISCLAIMER_LINE = "Dit rapport is uitsluitend bedoeld voor informatieve en educatieve doeleinden; zie de disclaimer aan het einde."
NL_FINAL_DISCLAIMER = "Dit rapport is uitsluitend bedoeld voor informatieve en educatieve doeleinden."

WEEKDAYS_NL = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
MONTHS_NL = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]

EN_TO_NL_HTML_LABELS = {
    "WEEKLY INDICES REVIEW": "WEEKLY INDEX REVIEW",
    "Investor Report": "Beleggersrapport",
    "Analyst Report": "Analistenrapport",
    "PART II": "DEEL II",
    "Research depth, scenario framing and implementation detail": "Onderzoeksdiepte, scenario’s en implementatiedetail",
    "Primary regime": "Primair regime",
    "Geopolitical regime": "Geopolitiek regime",
    "Main takeaway": "Kernboodschap",
    "Executive Summary": "Samenvatting",
    "Portfolio Action Snapshot": "Portefeuille-acties in één oogopslag",
    "Global Regime Dashboard": "Wereldwijd regimedashboard",
    "Index Opportunity Board": "Indexkansenbord",
    "Key Risks / Invalidators": "Belangrijkste risico’s / ontkrachters",
    "Bottom Line": "Kernconclusie",
    "Equity Curve and Portfolio Development": "Vermogenscurve en portefeuilleontwikkeling",
    "Regional / Style Allocation Map": "Regionale en stijlallocatiekaart",
    "Second-Order Effects Map": "Tweede-orde-effectenkaart",
    "Current Position Review": "Beoordeling huidige posities",
    "Best New Index Opportunities": "Beste nieuwe indexkansen",
    "Portfolio Rotation Plan": "Portefeuillerotatieplan",
    "Final Action Table": "Definitieve actietabel",
    "Position Changes Executed This Run": "Positiewijzigingen in deze run",
    "Current Portfolio Holdings and Cash": "Huidige portefeuilleposities en cash",
    "Continuity Input for Next Run": "Continuïteitsinvoer voor de volgende run",
    "Recommendation": "Aanbeveling",
    "Tickers / notes": "Tickers / opmerkingen",
    "Best replacements to fund": "Beste vervangingen om te monitoren",
    "Best replacements to monitor": "Beste vervangingen om te monitoren",
    "Top 3 actions this week": "Top 3 acties deze week",
    "Top 3 risks this week": "Top 3 risico’s deze week",
    ">Add<": ">Toevoegen<",
    ">Hold<": ">Houden<",
    ">Hold but replaceable<": ">Houden, maar vervangbaar<",
    ">Reduce<": ">Verlagen<",
    ">Close<": ">Sluiten<",
}

NL_TO_EN_HEADINGS = {
    "# Weekly Index Review": "# Weekly Indices Review",
    "## 1. Samenvatting": "## 1. Executive Summary",
    "## 2. Portefeuille-acties in één oogopslag": "## 2. Portfolio Action Snapshot",
    "## 3. Wereldwijd regimedashboard": "## 3. Global Regime Dashboard",
    "## 4. Indexkansenbord": "## 4. Index Opportunity Board",
    "## 5. Belangrijkste risico’s / ontkrachters": "## 5. Key Risks / Invalidators",
    "## 6. Kernconclusie": "## 6. Bottom Line",
    "## 7. Vermogenscurve en portefeuilleontwikkeling": "## 7. Equity Curve and Portfolio Development",
    "## 8. Regionale en stijlallocatiekaart": "## 8. Regional / Style Allocation Map",
    "## 9. Tweede-orde-effectenkaart": "## 9. Second-Order Effects Map",
    "## 10. Beoordeling huidige posities": "## 10. Current Position Review",
    "## 11. Beste nieuwe indexkansen": "## 11. Best New Index Opportunities",
    "## 12. Portefeuillerotatieplan": "## 12. Portfolio Rotation Plan",
    "## 13. Definitieve actietabel": "## 13. Final Action Table",
    "## 14. Positiewijzigingen in deze run": "## 14. Position Changes Executed This Run",
    "## 15. Huidige portefeuilleposities en cash": "## 15. Current Portfolio Holdings and Cash",
    "## 16. Continuïteitsinvoer voor de volgende run": "## 16. Continuity Input for Next Run",
    "## 17. Disclaimer": "## 17. Disclaimer",
}

NL_TO_EN_H3 = {
    "### Beste vervangingen om te monitoren": "### Best replacements to monitor",
    "### Top 3 acties deze week": "### Top 3 actions this week",
    "### Top 3 risico’s deze week": "### Top 3 risks this week",
}

ACTION_ROW_LABELS = {
    "Toevoegen": "Add",
    "Houden": "Hold",
    "Houden, maar vervangbaar": "Hold but replaceable",
    "Houden, onder herbeoordeling": "Hold but replaceable",
    "Verlagen": "Reduce",
    "Sluiten": "Close",
}

_ORIG_VALIDATE_REPORT = _base.validate_report
_ORIG_VALIDATE_EMAIL_BODY = _base.validate_email_body
_ORIG_PARSE_REPORT_DATE = _base.parse_report_date
_PATCHED_BUILD_REPORT_HTML = _base.build_report_html


def _is_dutch_report(md_text: str) -> bool:
    return "## 1. Samenvatting" in md_text or "Nederlandse conceptversie" in md_text


def _token_to_iso(token: str) -> str:
    return f"20{token[0:2]}-{token[2:4]}-{token[4:6]}"


def _iso_to_nl(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{WEEKDAYS_NL[dt.weekday()]} {dt.day} {MONTHS_NL[dt.month - 1]} {dt.year}"


def _tv_url(ticker: str) -> str:
    return f"https://www.tradingview.com/chart/?symbol={quote(ticker, safe='')}"


def _ticker_anchor(ticker: str) -> str:
    return f'<a href="{_tv_url(ticker)}" target="_blank" rel="noopener noreferrer">{ticker}</a>'


def _linkify_text_segment(segment: str) -> str:
    def repl(match: re.Match[str]) -> str:
        token = match.group(1)
        return _ticker_anchor(token) if token in HTML_LINKABLE_TICKERS else token
    return HTML_TOKEN_RE.sub(repl, segment)


def _linkify_html_tickers(html: str) -> str:
    """Link visible ticker tokens in final HTML, never in markdown source.

    This mirrors the Weekly ETF delivery-layer pattern: keep report markdown clean
    and add links during rendering. It prevents raw markdown links such as
    `[QQQ](...)` from appearing in custom HTML blocks while still satisfying the
    clickable ticker contract.
    """
    html = MARKDOWN_TV_LINK_LITERAL_RE.sub(lambda m: _ticker_anchor(m.group(1)), html)
    parts = HTML_TAG_RE.split(html)
    out: list[str] = []
    in_anchor = False
    in_protected = False
    for part in parts:
        if not part:
            continue
        if part.startswith("<") and part.endswith(">"):
            lower = part.lower()
            if lower.startswith("<a ") or lower.startswith("<a>"):
                in_anchor = True
            elif lower.startswith("</a"):
                in_anchor = False
            elif lower.startswith("<script") or lower.startswith("<style"):
                in_protected = True
            elif lower.startswith("</script") or lower.startswith("</style"):
                in_protected = False
            out.append(part)
        elif in_anchor or in_protected:
            out.append(part)
        else:
            out.append(_linkify_text_segment(part))
    return "".join(out)


def _normalize_dutch_heading_for_renderer(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("# Weekly Index Review"):
        return "# Weekly Indices Review"
    for nl, en in NL_TO_EN_HEADINGS.items():
        if stripped == nl:
            return en
    for nl, en in NL_TO_EN_H3.items():
        if stripped == nl:
            return en
    return line


def _convert_section2_table_rows(lines: list[str]) -> list[str]:
    result: list[str] = []
    in_section2 = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## 2. "):
            in_section2 = True
            result.append(line)
            continue
        if in_section2 and stripped.startswith("## "):
            in_section2 = False
            result.append(line)
            continue
        if in_section2 and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) >= 2:
                label = cells[0]
                value = cells[1]
                if label in {"Aanbeveling", "---"} or set(label) <= {"-", ":"}:
                    continue
                english_label = ACTION_ROW_LABELS.get(label)
                if english_label:
                    result.append(f"### {english_label}")
                    result.append(f"- {value}")
                    continue
        result.append(line)
    return result


def _nl_markdown_for_english_renderer(md_text: str) -> str:
    lines = [_normalize_dutch_heading_for_renderer(line) for line in md_text.splitlines()]
    lines = _convert_section2_table_rows(lines)
    text = "\n".join(lines)
    replacements = {
        "**Primair regime:**": "**Primary regime:**",
        "**Geopolitiek regime:**": "**Geopolitical regime:**",
        "**Kernboodschap:**": "**Main takeaway:**",
        "**Kernboodschap**": "**Main takeaway**",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _localize_rendered_html(html: str) -> str:
    for source, target in sorted(EN_TO_NL_HTML_LABELS.items(), key=lambda x: len(x[0]), reverse=True):
        html = html.replace(source, target)
    html = html.replace(_base.DISCLAIMER_LINE, NL_DISCLAIMER_LINE)
    return _linkify_html_tickers(html)


def validate_report(md_text: str) -> None:
    if not _is_dutch_report(md_text):
        _ORIG_VALIDATE_REPORT(md_text)
        return
    missing = [h for h in NL_REQUIRED_HEADINGS if h not in md_text]
    if missing:
        raise RuntimeError("Dutch report is missing required headings: " + ", ".join(missing))
    if NL_DISCLAIMER_LINE not in md_text:
        raise RuntimeError("Dutch disclaimer line is missing from report body.")
    if "EQUITY_CURVE_CHART_PLACEHOLDER" not in md_text:
        raise RuntimeError("Equity curve placeholder line is missing.")
    if NL_FINAL_DISCLAIMER not in md_text:
        raise RuntimeError("Dutch final disclaimer body is missing.")
    if not NL_LONG_DATE_RE.search(md_text):
        raise RuntimeError("Dutch report is missing a localized Dutch long date.")


def parse_report_date(md_text: str, report_path: Path | None = None) -> str:
    if report_path:
        match = NL_REPORT_RE.match(report_path.name)
        if match:
            return _token_to_iso(match.group(1))
    return _ORIG_PARSE_REPORT_DATE(md_text, report_path)


def format_full_date(date_str: str) -> str:
    return _iso_to_nl(date_str)


def validate_email_body(html_body: str, md_text: str | None = None) -> None:
    if md_text and not _is_dutch_report(md_text):
        _ORIG_VALIDATE_EMAIL_BODY(html_body, md_text)
        return
    html_lower = html_body.lower()
    required_groups = [
        ["weekly index review"],
        ["samenvatting"],
        ["portefeuille-acties", "aanbeveling"],
        ["indexkansenbord"],
        ["kernconclusie"],
        ["huidige portefeuilleposities en cash"],
        ["continuïteitsinvoer"],
    ]
    missing = [group for group in required_groups if not any(token in html_lower for token in group)]
    if missing:
        raise RuntimeError("Dutch HTML body is missing required content groups: " + str(missing))
    if md_text:
        plain_html = _base.html_to_plain_text(html_body)
        plain_md = _base.html_to_plain_text(_base.mdlib.markdown(md_text, extensions=["tables", "sane_lists", "fenced_code"]))
        if len(plain_html) < 0.58 * len(plain_md):
            raise RuntimeError(
                f"Dutch HTML body appears too short relative to the full report: html_chars={len(plain_html)} md_chars={len(plain_md)}"
            )


def build_report_html(md_text: str, report_date_str: str, image_src: str | None = None, render_mode: str = "email") -> str:
    if not _is_dutch_report(md_text):
        return _PATCHED_BUILD_REPORT_HTML(md_text, report_date_str, image_src=image_src, render_mode=render_mode)
    render_md = _nl_markdown_for_english_renderer(md_text)
    html = _PATCHED_BUILD_REPORT_HTML(render_md, report_date_str, image_src=image_src, render_mode=render_mode)
    return _localize_rendered_html(html)


_base.validate_report = validate_report
_base.parse_report_date = parse_report_date
_base.format_full_date = format_full_date
_base.validate_email_body = validate_email_body
_base.build_report_html = build_report_html
_base.TITLE = "Weekly Index Review"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--language", choices=["auto", "en", "nl"], default="auto")
    args = parser.parse_args()

    output_dir = Path("output_indices")
    report_path = Path(args.report_path)
    if not report_path.exists():
        raise FileNotFoundError(f"Explicit report path does not exist: {report_path}")

    assets = _base.generate_delivery_assets(output_dir, report_path)
    manifest_path = report_path.with_name(report_path.stem + "_delivery_manifest.txt")

    if args.validate_only:
        _base.write_manifest(
            manifest_path,
            report_path.name,
            "validation_only",
            [assets["html_path"].name, assets["pdf_path"].name],
            "validation_only",
        )
        print(f"BILINGUAL_VALIDATION_OK | report={report_path.name} | manifest={manifest_path.name}")
        return

    sent, attachment_names, recipient = _base.maybe_send_email(assets)
    if sent:
        _base.write_manifest(manifest_path, report_path.name, recipient, attachment_names, "delivery_ok")
        print(f"BILINGUAL_DELIVERY_OK | report={report_path.name} | recipient={recipient} | manifest={manifest_path.name}")
    else:
        _base.write_manifest(manifest_path, report_path.name, recipient, [assets["html_path"].name, assets["pdf_path"].name], recipient)
        print(f"BILINGUAL_RENDER_OK | report={report_path.name} | delivery={recipient} | manifest={manifest_path.name}")


if __name__ == "__main__":
    main()
