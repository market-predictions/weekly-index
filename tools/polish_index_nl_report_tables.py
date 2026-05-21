#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

SECTION_RE = re.compile(r"(^##\s+(\d+)\.\s+.*?$)", re.M)
EXTRA_EMPTY_STATUS_PIPE_RE = re.compile(
    r"(\|\s*\d+\.\d{2}\s*/5\s*\([^)]+\)\s*)\|\s*\|\s*"
    r"(Actief geselecteerd|Interessant, maar nog onvoldoende overtuiging|Niet aantrekkelijk genoeg deze week)\s*\|"
)


def _section_bounds(text: str, number: int) -> tuple[int, int] | None:
    matches = list(SECTION_RE.finditer(text))
    for idx, match in enumerate(matches):
        if int(match.group(2)) == number:
            return match.start(), matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
    return None


def _cell_count(markdown_row: str) -> int:
    return len([cell for cell in markdown_row.strip().strip("|").split("|")])


def _fix_score_status_pipe(text: str) -> str:
    # v2 score decoration once produced: | 2.82 /5 (Hoog) | | Actief geselecteerd | reason |
    # That creates an empty Status column and pushes the real reason out of the table contract.
    return EXTRA_EMPTY_STATUS_PIPE_RE.sub(lambda m: f"{m.group(1)}| {m.group(2)} |", text)


def _detach_omitted_challenger_note(text: str) -> str:
    # Python-Markdown's table extension needs a blank line after a table. Without it,
    # the compact-board note can render as a one-cell table row with a huge empty area.
    return re.sub(
        r"(?<!\n)\n(Het bord blijft bewust compact\. De sterkste weggelaten regionale uitdager deze run is)",
        r"\n\n\1",
        text,
    )


def _validate_section4_table(text: str, path: Path) -> None:
    bounds = _section_bounds(text, 4)
    if not bounds:
        raise SystemExit(f"{path}: missing section 4")

    section = text[bounds[0]:bounds[1]]
    lines = section.splitlines()
    table_start = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("| Portefeuillesleeve |"):
            table_start = idx
            break
    if table_start is None:
        raise SystemExit(f"{path}: missing Section 4 opportunity-board table")

    table_lines: list[str] = []
    for line in lines[table_start:]:
        stripped = line.strip()
        if not stripped:
            break
        if not stripped.startswith("|"):
            break
        table_lines.append(stripped)

    if len(table_lines) < 3:
        raise SystemExit(f"{path}: Section 4 opportunity-board table has too few rows")

    expected = _cell_count(table_lines[0])
    for idx, row in enumerate(table_lines, table_start + 1):
        actual = _cell_count(row)
        if actual != expected:
            raise SystemExit(
                f"{path}: malformed Section 4 table row {idx}: expected {expected} cells, got {actual}: {row}"
            )

    if "Het bord blijft bewust compact" in "\n".join(table_lines):
        raise SystemExit(f"{path}: omitted-challenger note is still inside the Section 4 table")

    if "\n\nHet bord blijft bewust compact." not in section:
        raise SystemExit(f"{path}: omitted-challenger note is not separated from the Section 4 table by a blank line")


def polish(text: str) -> str:
    text = _fix_score_status_pipe(text)
    text = _detach_omitted_challenger_note(text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Polish Dutch Weekly Index markdown tables before render.")
    parser.add_argument("--nl-report", required=True)
    args = parser.parse_args()

    path = Path(args.nl_report)
    original = path.read_text(encoding="utf-8")
    polished = polish(original)
    _validate_section4_table(polished, path)

    if polished != original:
        path.write_text(polished.rstrip() + "\n", encoding="utf-8")
        print(f"INDEX_NL_TABLE_POLISH_APPLIED | report={path.name}")
    else:
        print(f"INDEX_NL_TABLE_POLISH_OK | report={path.name}")


if __name__ == "__main__":
    main()
