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
]
REPORT_RE = re.compile(r"weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")


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
    if section11:
        lower11 = section11.lower()
        if "long-side" in lower11 and "inverse" in lower11:
            if "best defensive" not in lower11 and "defensive / inverse" not in lower11:
                raise RuntimeError("Index compactness contract failed: inverse candidates appear near long board without clear defensive separation.")

    print(f"INDEX_COMPACTNESS_CONTRACT_OK | report={path.name}")


if __name__ == "__main__":
    validate()
