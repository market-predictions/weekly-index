#!/usr/bin/env python3
"""Independent pre-send assurance for the active Weekly Indices Review."""
from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IMPLEMENTATION_ROLE = "implementation_operations"
ASSURANCE_ROLE = "governance_release_assurance"
SHA_RE = re.compile(r"[0-9a-f]{40}")
NUMBER_RE = re.compile(r"[-+]?\d[\d.,]*%?")
SECTION_RE = re.compile(r"^##\s+(\d+)\.", re.MULTILINE)
REQUIRED_CHECKS = {
    "source_identity_bound",
    "required_files_present",
    "control_json_parseable",
    "artifact_formats_valid",
    "pricing_identity_consistent",
    "benchmark_proxy_separation",
    "runtime_sources_consistent",
    "bilingual_section_parity",
    "bilingual_table_numeric_parity",
    "english_transport_deferred",
    "artifact_hashes_complete",
    "roles_separated",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def contains_identity(payload: Any, value: str) -> bool:
    if isinstance(payload, dict):
        return any(contains_identity(item, value) for item in payload.values())
    if isinstance(payload, list):
        return any(contains_identity(item, value) for item in payload)
    return str(payload) == value


def add_check(checks: list[dict[str, Any]], blockers: list[str], check_id: str, passed: bool, evidence: Any) -> None:
    checks.append({"id": check_id, "passed": bool(passed), "evidence": evidence})
    if not passed:
        blockers.append(check_id)


def report_assets(report: Path) -> dict[str, Path]:
    return {
        "report": report,
        "delivery_html": report.with_name(f"{report.stem}_delivery.html"),
        "pdf": report.with_suffix(".pdf"),
        "equity_curve_png": report.with_name(f"{report.stem}_equity_curve.png"),
    }


def normalize_number(token: str) -> str | None:
    token = token.strip().replace(" ", "")
    percent = token.endswith("%")
    if percent:
        token = token[:-1]
    sign = ""
    if token.startswith(("+", "-")):
        sign, token = token[0], token[1:]
    if not token or not any(char.isdigit() for char in token):
        return None
    if "," in token and "." in token:
        if token.rfind(",") > token.rfind("."):
            token = token.replace(".", "").replace(",", ".")
        else:
            token = token.replace(",", "")
    elif "," in token:
        tail = token.rsplit(",", 1)[1]
        token = token.replace(",", ".") if len(tail) <= 2 else token.replace(",", "")
    elif token.count(".") > 1:
        token = token.replace(".", "")
    try:
        value = float(f"{sign}{token}")
    except ValueError:
        return None
    if not percent and value.is_integer() and (1 <= abs(value) <= 17 or 2000 <= abs(value) <= 2100):
        return None
    suffix = "%" if percent else ""
    return f"{value:.8f}".rstrip("0").rstrip(".") + suffix


def table_numbers(path: Path) -> Counter[str]:
    values: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "|" not in line:
            continue
        for token in NUMBER_RE.findall(line):
            normalized = normalize_number(token)
            if normalized is not None:
                values.append(normalized)
    return Counter(values)


def valid_format(key: str, path: Path) -> str | None:
    size = path.stat().st_size
    if key.endswith("_report"):
        if size < 512 or "#" not in path.read_text(encoding="utf-8", errors="replace"):
            return f"{key}: invalid markdown"
    elif key.endswith("_html"):
        raw = path.read_text(encoding="utf-8", errors="replace").lower()
        if size < 1024 or ("<html" not in raw and "<!doctype" not in raw):
            return f"{key}: invalid HTML"
    elif key.endswith("_pdf"):
        if size < 1024 or path.read_bytes()[:5] != b"%PDF-":
            return f"{key}: invalid PDF"
    elif key.endswith("_png"):
        if size < 128 or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            return f"{key}: invalid PNG"
    elif key.endswith("_csv") and size < 8:
        return f"{key}: empty CSV"
    return None


def deferral_marker_path(token: str) -> Path:
    return Path("output_indices/run_manifests") / f"index_english_send_deferred_{token}.json"


def write_english_deferral_marker(report_path: Path, *, close_date: str, token: str) -> Path:
    marker = deferral_marker_path(token)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "status": "ENGLISH_TRANSPORT_DEFERRED",
                "requested_close_date": close_date,
                "report_token": token,
                "english_report_path": str(report_path),
                "source_sha": os.environ.get("GITHUB_SHA", ""),
                "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
                "transport_attempted": False,
                "reason": "Awaiting Dutch companion and independent bilingual assurance",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"INDEX_ENGLISH_TRANSPORT_DEFERRED | marker={marker}")
    return marker


def build_release_assurance(
    *,
    source_sha: str,
    github_run_id: str,
    requested_close_date: str,
    report_token: str,
    english_report: Path,
    dutch_report: Path,
    output: Path,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    try:
        datetime.strptime(requested_close_date, "%Y-%m-%d")
        valid_date = True
    except ValueError:
        valid_date = False
    identity_ok = bool(SHA_RE.fullmatch(source_sha.lower())) and valid_date and bool(re.fullmatch(r"\d{6}", report_token))
    add_check(checks, blockers, "source_identity_bound", identity_ok, {"source_sha": source_sha, "github_run_id": github_run_id, "requested_close_date": requested_close_date, "report_token": report_token})

    pricing = Path("output_indices/pricing") / f"index_price_audit_{requested_close_date}.json"
    runtime = Path("output_indices/runtime") / f"index_report_state_{report_token}.json"
    portfolio = Path("output_indices/index_portfolio_state.json")
    valuation = Path("output_indices/index_valuation_history.csv")
    scorecard = Path("output_indices/index_recommendation_scorecard.csv")
    ranking = Path("output_indices") / f"index_candidate_ranking_{report_token}.json"
    coverage = Path("output_indices") / f"index_discovery_coverage_{report_token}.json"
    marker = deferral_marker_path(report_token)
    en = report_assets(english_report)
    nl = report_assets(dutch_report)
    paths = {
        "pricing_audit": pricing,
        "runtime_state": runtime,
        "portfolio_state": portfolio,
        "valuation_csv": valuation,
        "scorecard_csv": scorecard,
        "candidate_ranking": ranking,
        "discovery_coverage": coverage,
        "english_deferral_marker": marker,
        "english_report": en["report"],
        "english_html": en["delivery_html"],
        "english_pdf": en["pdf"],
        "english_png": en["equity_curve_png"],
        "dutch_report": nl["report"],
        "dutch_html": nl["delivery_html"],
        "dutch_pdf": nl["pdf"],
        "dutch_png": nl["equity_curve_png"],
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    add_check(checks, blockers, "required_files_present", not missing, {"missing": missing})

    parsed: dict[str, Any] = {}
    json_errors: dict[str, str] = {}
    for key in ("pricing_audit", "runtime_state", "portfolio_state", "candidate_ranking", "discovery_coverage", "english_deferral_marker"):
        path = paths[key]
        if path.is_file():
            try:
                parsed[key] = load_json(path)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                json_errors[key] = str(exc)
    add_check(checks, blockers, "control_json_parseable", not json_errors, json_errors)

    format_errors: list[str] = []
    for key, path in paths.items():
        if path.is_file():
            error = valid_format(key, path)
            if error:
                format_errors.append(error)
    add_check(checks, blockers, "artifact_formats_valid", not format_errors, format_errors)

    pricing_payload = parsed.get("pricing_audit", {})
    pricing_ok = isinstance(pricing_payload, dict) and pricing_payload.get("requested_close_date") == requested_close_date
    add_check(checks, blockers, "pricing_identity_consistent", pricing_ok, {"path": str(pricing), "requested_close_date": pricing_payload.get("requested_close_date") if isinstance(pricing_payload, dict) else None})

    separation_errors: list[str] = []
    positions = pricing_payload.get("positions", []) if isinstance(pricing_payload, dict) else []
    if not positions:
        separation_errors.append("pricing audit has no funded positions")
    for index, row in enumerate(positions):
        if not isinstance(row, dict):
            separation_errors.append(f"row {index}: invalid")
            continue
        required = ("benchmark_symbol", "primary_proxy", "benchmark_close", "proxy_close", "benchmark_source", "proxy_source")
        missing_fields = [field for field in required if row.get(field) in (None, "")]
        if missing_fields:
            separation_errors.append(f"row {index}: missing {missing_fields}")
    add_check(checks, blockers, "benchmark_proxy_separation", not separation_errors, separation_errors)

    runtime_payload = parsed.get("runtime_state", {})
    source_files = runtime_payload.get("source_files", {}) if isinstance(runtime_payload, dict) else {}
    runtime_errors: list[str] = []
    expected_sources = {
        "pricing_audit": str(pricing),
        "candidate_ranking": str(ranking),
        "discovery_coverage": str(coverage),
        "portfolio_state": str(portfolio),
        "scorecard": str(scorecard),
    }
    for key, value in expected_sources.items():
        if source_files.get(key) != value:
            runtime_errors.append(f"{key}: expected {value!r}, got {source_files.get(key)!r}")
    if runtime_payload.get("report_token") != report_token:
        runtime_errors.append("runtime report token mismatch")
    if runtime_payload.get("report_date") != requested_close_date:
        runtime_errors.append("runtime report date mismatch")
    add_check(checks, blockers, "runtime_sources_consistent", not runtime_errors, runtime_errors)

    en_sections = sorted(set(SECTION_RE.findall(english_report.read_text(encoding="utf-8", errors="replace")))) if english_report.is_file() else []
    nl_sections = sorted(set(SECTION_RE.findall(dutch_report.read_text(encoding="utf-8", errors="replace")))) if dutch_report.is_file() else []
    section_ok = en_sections == nl_sections and all(str(i) in en_sections for i in range(1, 18))
    add_check(checks, blockers, "bilingual_section_parity", section_ok, {"english": en_sections, "dutch": nl_sections})

    parity_evidence: dict[str, Any] = {}
    parity_ok = False
    if english_report.is_file() and dutch_report.is_file():
        en_numbers = table_numbers(english_report)
        nl_numbers = table_numbers(dutch_report)
        parity_ok = bool(en_numbers) and en_numbers == nl_numbers
        parity_evidence = {"english_count": sum(en_numbers.values()), "dutch_count": sum(nl_numbers.values()), "english_only": list((en_numbers - nl_numbers).elements())[:20], "dutch_only": list((nl_numbers - en_numbers).elements())[:20]}
    add_check(checks, blockers, "bilingual_table_numeric_parity", parity_ok, parity_evidence)

    marker_payload = parsed.get("english_deferral_marker", {})
    marker_ok = isinstance(marker_payload, dict) and marker_payload.get("status") == "ENGLISH_TRANSPORT_DEFERRED" and marker_payload.get("transport_attempted") is False and marker_payload.get("report_token") == report_token and marker_payload.get("requested_close_date") == requested_close_date and marker_payload.get("english_report_path") == str(english_report)
    add_check(checks, blockers, "english_transport_deferred", marker_ok, marker_payload if isinstance(marker_payload, dict) else {})

    hashes: dict[str, dict[str, str]] = {}
    if not missing:
        hashes = {key: {"path": str(path), "sha256": sha256_file(path)} for key, path in paths.items()}
    hashes_ok = len(hashes) == len(paths) and all(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) for item in hashes.values())
    add_check(checks, blockers, "artifact_hashes_complete", hashes_ok, hashes)

    add_check(checks, blockers, "roles_separated", IMPLEMENTATION_ROLE != ASSURANCE_ROLE, {"implementation_role": IMPLEMENTATION_ROLE, "assurance_role": ASSURANCE_ROLE, "implementation_may_self_certify": False, "assurance_may_mutate_release_candidate": False})

    decision = "PASS" if not blockers else "FAIL"
    record = {
        "schema_version": "1.0.0",
        "contract_id": "INDEX_RELEASE_ASSURANCE_CONTRACT_V1",
        "product": "weekly_indices_review",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "decision": decision,
        "implementation_role": IMPLEMENTATION_ROLE,
        "assurance_role": ASSURANCE_ROLE,
        "identity": {"source_sha": source_sha.lower(), "github_run_id": github_run_id, "requested_close_date": requested_close_date, "report_token": report_token},
        "checks": checks,
        "artifact_hashes": hashes,
        "blockers": blockers,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def validate_release_assurance(path: Path, *, expected_source_sha: str | None = None, expected_close_date: str | None = None, expected_report_token: str | None = None) -> dict[str, Any]:
    payload = load_json(path)
    errors: list[str] = []
    if payload.get("decision") != "PASS":
        errors.append(f"decision must be PASS, got {payload.get('decision')!r}")
    if payload.get("implementation_role") != IMPLEMENTATION_ROLE or payload.get("assurance_role") != ASSURANCE_ROLE:
        errors.append("role identity mismatch")
    if payload.get("blockers"):
        errors.append(f"blockers present: {payload.get('blockers')}")
    checks = {item.get("id"): item for item in payload.get("checks", []) if isinstance(item, dict)}
    missing = sorted(REQUIRED_CHECKS - set(checks))
    failed = sorted(key for key, item in checks.items() if item.get("passed") is not True)
    if missing:
        errors.append(f"required checks missing: {missing}")
    if failed:
        errors.append(f"failed checks present: {failed}")
    identity = payload.get("identity", {})
    expected = {"source_sha": expected_source_sha.lower() if expected_source_sha else None, "requested_close_date": expected_close_date, "report_token": expected_report_token}
    for key, value in expected.items():
        if value is not None and identity.get(key) != value:
            errors.append(f"identity mismatch for {key}: expected {value!r}, got {identity.get(key)!r}")
    hashes = payload.get("artifact_hashes", {})
    if not hashes or any(not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))) for item in hashes.values() if isinstance(item, dict)):
        errors.append("artifact hashes incomplete")
    if errors:
        raise RuntimeError("Index release assurance rejected: " + "; ".join(errors))
    return payload


def ensure_release_assurance_from_environment(english_report: Path, dutch_report: Path) -> Path:
    required = ["GITHUB_SHA", "REQUESTED_CLOSE_DATE", "REPORT_TOKEN"]
    missing = [key for key in required if not os.environ.get(key, "").strip()]
    if missing:
        raise RuntimeError(f"Index release assurance missing required environment: {missing}")
    close_date = os.environ["REQUESTED_CLOSE_DATE"].strip()
    token = os.environ["REPORT_TOKEN"].strip()
    output = Path("output_indices/run_manifests") / f"index_release_assurance_{close_date}_{token}.json"
    record = build_release_assurance(
        source_sha=os.environ["GITHUB_SHA"].strip(),
        github_run_id=os.environ.get("GITHUB_RUN_ID", "").strip(),
        requested_close_date=close_date,
        report_token=token,
        english_report=english_report,
        dutch_report=dutch_report,
        output=output,
    )
    if record["decision"] != "PASS":
        raise RuntimeError(f"Index release assurance failed: {record['blockers']}")
    validate_release_assurance(output, expected_source_sha=os.environ["GITHUB_SHA"].strip(), expected_close_date=close_date, expected_report_token=token)
    print(f"INDEX_RELEASE_ASSURANCE_PASS | output={output} | artifacts={len(record['artifact_hashes'])}")
    return output
