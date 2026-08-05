from __future__ import annotations

"""Guarded English stage for the Weekly Indices Review.

Imported callers receive the preserved renderer module itself. Direct English
transport is deferred only when this path is executed as the workflow entrypoint.
"""

import os
import subprocess
import sys
from pathlib import Path

import send_index_report_tv_analyst_distinct_legacy as _legacy


if __name__ != "__main__":
    sys.modules[__name__] = _legacy
else:
    from tools.index_release_assurance import write_english_deferral_marker

    def _argument_value(flag: str) -> str:
        try:
            index = sys.argv.index(flag)
        except ValueError as exc:
            raise RuntimeError(f"Missing required argument: {flag}") from exc
        if index + 1 >= len(sys.argv):
            raise RuntimeError(f"Missing value for argument: {flag}")
        return sys.argv[index + 1]

    if "--validate-only" in sys.argv:
        _legacy.main()
    else:
        report_path = Path(_argument_value("--report-path"))
        validation_args = [
            sys.executable,
            "send_index_report_tv_analyst_distinct_legacy.py",
            *sys.argv[1:],
            "--validate-only",
        ]
        subprocess.run(validation_args, check=True)

        close_date = os.environ.get("REQUESTED_CLOSE_DATE", "").strip()
        token = os.environ.get("REPORT_TOKEN", "").strip()
        if not close_date or not token:
            raise RuntimeError("English transport deferral requires REQUESTED_CLOSE_DATE and REPORT_TOKEN.")
        marker = write_english_deferral_marker(report_path, close_date=close_date, token=token)
        print(f"INDEX_ENGLISH_SEND_STAGE_COMPLETE | status=deferred | marker={marker}")
