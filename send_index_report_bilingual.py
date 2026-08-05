#!/usr/bin/env python3
from __future__ import annotations

"""Guarded bilingual transport entrypoint for Weekly Indices Review."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import send_index_report_bilingual_legacy as _legacy
from tools.index_release_assurance import ensure_release_assurance_from_environment

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

    dutch_report = Path(_argument_value("--report-path"))
    token = os.environ.get("REPORT_TOKEN", "").strip()
    close_date = os.environ.get("REQUESTED_CLOSE_DATE", "").strip()
    english_raw = os.environ.get("REPORT_PATH", "").strip()
    if not token or not close_date or not english_raw:
        raise RuntimeError("Bilingual transport requires REPORT_TOKEN, REQUESTED_CLOSE_DATE and REPORT_PATH.")
    english_report = Path(english_raw)

    assurance_path = ensure_release_assurance_from_environment(english_report, dutch_report)
    print(f"INDEX_GOVERNANCE_PASS_PRE_SEND | assurance={assurance_path}")

    english_env = dict(os.environ)
    english_env["MRKT_RPRTS_SUBJECT_PREFIX"] = "Weekly Indices Review"
    subprocess.run(
        [sys.executable, "send_index_report_tv_analyst_distinct_legacy.py", "--report-path", str(english_report)],
        check=True,
        env=english_env,
    )
    subprocess.run(
        [sys.executable, "send_index_report_bilingual_legacy.py", *sys.argv[1:]],
        check=True,
        env=dict(os.environ),
    )

    receipt = Path("output_indices/run_manifests") / f"index_transport_receipt_{close_date}_{token}.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "status": "TRANSPORT_SENT_UNVERIFIED",
                "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                "requested_close_date": close_date,
                "report_token": token,
                "assurance_path": str(assurance_path),
                "english_report_path": str(english_report),
                "dutch_report_path": str(dutch_report),
                "independent_receipt_confirmed": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"INDEX_TRANSPORT_SENT_UNVERIFIED | receipt={receipt}")


if __name__ == "__main__":
    main()
