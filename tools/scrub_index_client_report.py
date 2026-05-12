from __future__ import annotations

import re
from pathlib import Path

OUTPUT_DIR = Path("output_indices")
REPORT_RE = re.compile(r"weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")

REPLACEMENTS = {
    "TBD": "Under review",
    "production workflow should refresh": "the next review should confirm",
    "Production workflow should refresh": "The next review should confirm",
    "workflow pricing": "pricing",
    "Workflow pricing": "Pricing",
    "workflow artifact": "report input",
    "Workflow artifact": "Report input",
    "live repo state": "current portfolio state",
    "Live repo state": "Current portfolio state",
    "pricing/ranking rebuild": "pricing and ranking refresh",
    "Pricing/ranking rebuild": "Pricing and ranking refresh",
    "artifact rebuild": "evidence refresh",
    "Artifact rebuild": "Evidence refresh",
    "workflow evidence": "delivery evidence",
    "Workflow evidence": "Delivery evidence",
    "manifest evidence": "delivery receipt",
    "Manifest evidence": "Delivery receipt",
    "check-only": "validation",
    "board_capacity": "kept off the compact board by stronger candidates",
    "near_miss": "close challenger, not funded",
    "Near miss": "Close challenger, not funded",
    "ruled_out": "lower priority this run",
    "weak_relative_strength": "weak relative strength",
    "fragile_macro_alignment": "macro timing not strong enough",
    "insufficient_immediate_priority": "not urgent enough for capital this week",
}

REGEX_REPLACEMENTS = [
    (re.compile(r"production\s+workflow\s+should\s+refresh", re.I), "the next review should confirm"),
    (re.compile(r"workflow\s+pricing", re.I), "pricing"),
    (re.compile(r"pricing\s*/\s*ranking\s+rebuild", re.I), "pricing and ranking refresh"),
    (re.compile(r"artifact\s+rebuild", re.I), "evidence refresh"),
    (re.compile(r"live\s+repo\s+state", re.I), "current portfolio state"),
    (re.compile(r"\bTBD\b"), "Under review"),
    (re.compile(r"\b([A-Z]{2,5})(versus|together|and)\b"), r"\1 \2"),
    (re.compile(r"\b(and|versus)([A-Z]{2,5})\b"), r"\1 \2"),
    (re.compile(r"\n-\s*$", re.M), ""),
    (re.compile(r"\n{3,}"), "\n\n"),
]


def latest_report() -> Path:
    hits: list[tuple[str, int, Path]] = []
    for path in OUTPUT_DIR.glob("weekly_indices_review_*.md"):
        match = REPORT_RE.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or "1"), path))
    if not hits:
        raise RuntimeError("No weekly_indices_review_*.md report found")
    hits.sort(key=lambda item: (item[0], item[1]))
    return hits[-1][2]


def scrub(text: str) -> str:
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    for pattern, replacement in REGEX_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text.rstrip() + "\n"


def main() -> None:
    path = latest_report()
    before = path.read_text(encoding="utf-8")
    after = scrub(before)
    path.write_text(after, encoding="utf-8")
    print(f"INDEX_CLIENT_REPORT_SCRUB_OK | report={path.name} | changed={before != after}")


if __name__ == "__main__":
    main()
