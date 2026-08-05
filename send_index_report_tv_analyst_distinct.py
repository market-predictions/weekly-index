from __future__ import annotations

"""Guarded English stage for the Weekly Indices Review.

Validation remains identical to the preserved legacy implementation. Direct
English transport is deferred until the Dutch companion and bilingual assurance
are complete; the later bilingual entrypoint releases both messages.
"""

import os
import subprocess
import sys
from pathlib import Path

import send_index_report_tv_analyst_distinct_legacy as _legacy
from tools.index_release_assurance import write_english_deferral_marker

for _name, _value in vars(_legacy).items():
    if _name not in {"__name__", "__file__", "__package__", "__loader__", "__spec__"}:
        globals()[_name] = _value


def _argument_value(flag: str) -> str:
    try:
        index = sys.argv.index(flag)
    except ValueError as exc:
        raise RuntimeError(f"Missing required argument: {flag}") from exc
    if index + 1 >= len(sys.argv):
        raise RuntimeError(f"Missing value for argument: {flag}")
    return sys.argv[index + 1]


def main() -> None:
    if "--validate-only" in sys.argv:
        _legacy.main()
        return

    report_path = Path(_argument_value("--report-path"))
    validation_args = [sys.executable, "send_index_report_tv_analyst_distinct_legacy.py", *sys.argv[1:], "--validate-only"]
    subprocess.run(validation_args, check=True)

    close_date = os.environ.get("REQUESTED_CLOSE_DATE", "").strip()
    token = os.environ.get("REPORT_TOKEN", "").strip()
    if not close_date or not token:
        raise RuntimeError("English transport deferral requires REQUESTED_CLOSE_DATE and REPORT_TOKEN.")
    marker = write_english_deferral_marker(report_path, close_date=close_date, token=token)
    print(f"INDEX_ENGLISH_SEND_STAGE_COMPLETE | status=deferred | marker={marker}")


if __name__ == "__main__":
    main()
