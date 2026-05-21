#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

RAW_TV_MARKDOWN_RE = re.compile(
    r"\[[A-Z][A-Z0-9.\-]{1,11}\]\(https://www\.tradingview\.com/chart/\?symbol=[^)]+\)"
)
GENERIC_TV_MARKDOWN_RE = re.compile(
    r"\[[^\]\n]{1,160}\]\(https://www\.tradingview\.com/chart/\?symbol=[^)]+\)"
)
BROKEN_TV_MARKDOWN_RESIDUE_RE = re.compile(
    r"\]\(https://www\.tradingview\.com/chart/\?symbol="
)


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _snippet(text: str, index: int, width: int = 140) -> str:
    start = max(0, index - width // 2)
    end = min(len(text), index + width // 2)
    return text[start:end].replace("\n", " ").strip()


def _scan_file(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing file: {path}"]

    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[str] = []
    checks = [
        ("raw ticker TradingView markdown link", RAW_TV_MARKDOWN_RE),
        ("generic TradingView markdown-link residue", GENERIC_TV_MARKDOWN_RE),
        ("broken TradingView markdown-link tail", BROKEN_TV_MARKDOWN_RESIDUE_RE),
    ]
    for label, pattern in checks:
        for match in pattern.finditer(text):
            findings.append(
                f"{path}:{_line_number(text, match.start())}: {label}: {_snippet(text, match.start())}"
            )
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail if Dutch markdown or delivery HTML contains visible TradingView markdown-link residue."
    )
    parser.add_argument("--report-path", required=True, help="Dutch report markdown path")
    parser.add_argument(
        "--html-path",
        default=None,
        help="Optional explicit delivery HTML path; defaults to <report stem>_delivery.html",
    )
    args = parser.parse_args()

    report_path = Path(args.report_path)
    html_path = Path(args.html_path) if args.html_path else report_path.with_name(report_path.stem + "_delivery.html")

    findings: list[str] = []
    for path in [report_path, html_path]:
        findings.extend(_scan_file(path))

    if findings:
        raise SystemExit(
            "Markdown-style TradingView link residue detected; keep Dutch markdown clean and linkify only in final HTML.\n"
            + "\n".join(findings)
        )

    print(f"NO_MARKDOWN_LINK_RESIDUE_OK | report={report_path.name} | html={html_path.name}")


if __name__ == "__main__":
    main()
