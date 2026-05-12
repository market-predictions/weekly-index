from __future__ import annotations

import re
from pathlib import Path

OUTPUT_DIR = Path("output_indices")
FORBIDDEN_CLIENT_TOKENS = [
    "board_capacity",
    "near_miss",
    "ruled_out",
    "weak_relative_strength",
    "fragile_macro_alignment",
    "insufficient_immediate_priority",
    "check-only",
    "TBD",
    "production workflow should refresh",
    "workflow pricing",
    "workflow artifact",
    "live repo state",
    "pricing/ranking rebuild",
    "artifact rebuild",
]
REPORT_RE = re.compile(r"weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")
INVERSE_TERMS = [" rwm", " eum", " psq", " sh", " efz", "short russell", "short nasdaq", "short s&p"]


def _latest_report() -> Path | None:
    hits: list[tuple[str, int, Path]] = []
    for path in OUTPUT_DIR.glob("weekly_indices_review_*.md"):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or "1"), path))
    if not hits:
        return None
    hits.sort(key=lambda item: (item[0], item[1]))
    return hits[-1][2]


def _section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    next_heading = text.find("\n## ", start + len(heading))
    return text[start: next_heading if next_heading != -1 else len(text)]


def _between(text: str, start_marker: str, end_markers: list[str]) -> str:
    start = text.find(start_marker)
    if start == -1:
        return ""
    start += len(start_marker)
    candidates = [text.find(marker, start) for marker in end_markers]
    candidates = [idx for idx in candidates if idx != -1]
    end = min(candidates) if candidates else len(text)
    return text[start:end]


def _leaked_inverse_terms(text: str) -> list[str]:
    lower = " " + text.lower().replace("|", " ").replace("\n", " ") + " "
    return [term.strip() for term in INVERSE_TERMS if term in lower]


def validate() -> None:
    path = _latest_report()
    if path is None:
        raise RuntimeError("Index compactness contract failed: no weekly_indices_review_*.md report found.")
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    forbidden = [token for token in FORBIDDEN_CLIENT_TOKENS if token.lower() in lower]
    if forbidden:
        raise RuntimeError(f"Index compactness contract failed for {path.name}: raw artifact/process terms found: {', '.join(forbidden)}")

    section11 = _section(text, "## 11.")
    lower11 = section11.lower()
    if section11:
        if "long-side opportunities" not in lower11:
            raise RuntimeError("Index compactness contract failed: Section 11 missing Long-side Opportunities.")
        if "best defensive / inverse opportunities" not in lower11:
            raise RuntimeError("Index compactness contract failed: Section 11 missing Best Defensive / Inverse Opportunities.")
        if "alternative duel table" not in lower11:
            raise RuntimeError("Index compactness contract failed: Section 11 missing Alternative Duel Table.")

        # The Alternative Duel Table can explicitly include defensive/inverse duel
        # rows as long as they are labelled as such. The long-side opportunity
        # board is only the subsection before the Alternative Duel Table.
        long_board = _between(lower11, "long-side opportunities", ["alternative duel table", "best defensive / inverse opportunities"])
        leaked = _leaked_inverse_terms(long_board)
        if leaked:
            raise RuntimeError(
                "Index compactness contract failed: inverse candidates appear in long-side opportunity board: "
                + ", ".join(leaked)
            )

        alternative_duel = _between(lower11, "alternative duel table", ["best defensive / inverse opportunities"])
        defensive_rows_present = any(term in alternative_duel for term in [" rwm", " eum", " psq"])
        if defensive_rows_present and "defensive / inverse" not in alternative_duel:
            raise RuntimeError(
                "Index compactness contract failed: inverse candidates in Alternative Duel Table must be explicitly labelled Defensive / inverse."
            )

    print(f"INDEX_COMPACTNESS_CONTRACT_OK | report={path.name}")


if __name__ == "__main__":
    validate()
