from __future__ import annotations

import re
from pathlib import Path

from pricing_indices.run_pricing_pass import latest_completed_us_close_date

RUN_QUEUE_DIR = Path('control/run_queue')
REQUEST_RE = re.compile(r'^weekly_indices_report_request_.*\.md$')
DATE_RE = re.compile(r'^\s*requested_close_date\s*:\s*(\d{4}-\d{2}-\d{2})\s*$', re.M)


def latest_request_file() -> Path | None:
    if not RUN_QUEUE_DIR.exists():
        return None
    hits = [p for p in RUN_QUEUE_DIR.glob('weekly_indices_report_request_*.md') if REQUEST_RE.match(p.name)]
    if not hits:
        return None
    hits.sort(key=lambda p: p.name)
    return hits[-1]


def main() -> None:
    request = latest_request_file()
    if request:
        text = request.read_text(encoding='utf-8')
        match = DATE_RE.search(text)
        if match:
            print(match.group(1))
            return
    print(latest_completed_us_close_date())


if __name__ == '__main__':
    main()
