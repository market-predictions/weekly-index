from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .catalog import ALL_EXPOSURES

REPORT_RE = re.compile(r"weekly_indices_review_(\d{6})(?:_(\d{2}))?\.md$")
PLAN_RE = re.compile(r"index_recommendation_plan_(\d{6})(?:_(\d{2}))?\.json$")

GROUPS = {
    "U.S. core leadership": {"us_large_cap", "us_tech_leadership", "us_small_cap"},
    "U.S. factor / style alternatives": {"us_equal_weight", "us_quality_factor", "us_min_vol_factor", "us_value_factor"},
    "continental Europe": {"europe_large_cap", "germany_cyclicals", "france_large_cap", "spain_large_cap", "italy_large_cap", "netherlands_large_cap"},
    "UK": {"uk_large_cap"},
    "Switzerland": {"switzerland_large_cap"},
    "North America ex-U.S.": {"canada_large_cap"},
    "developed Asia-Pacific": {"japan_equities", "australia_large_cap"},
    "Korea / Taiwan": {"south_korea_large_cap", "taiwan_large_cap"},
    "Greater China": {"hong_kong_equities", "china_large_cap"},
    "India": {"india_large_cap"},
    "Latin America": {"brazil_large_cap", "mexico_large_cap"},
    "Africa": {"south_africa_large_cap"},
    "ASEAN": {"indonesia_large_cap"},
    "Middle East": {"saudi_large_cap"},
    "EM broad": {"em_broad"},
}

GROUP_BASE_SCORE = {
    "U.S. core leadership": 3.75,
    "U.S. factor / style alternatives": 3.28,
    "continental Europe": 3.35,
    "UK": 3.10,
    "Switzerland": 3.12,
    "North America ex-U.S.": 3.05,
    "developed Asia-Pacific": 3.45,
    "Korea / Taiwan": 3.30,
    "Greater China": 3.00,
    "India": 3.25,
    "Latin America": 2.95,
    "Africa": 2.70,
    "ASEAN": 2.85,
    "Middle East": 2.80,
    "EM broad": 3.20,
}

PROXY_ELIGIBILITY = {
    "core_holding": "Funded or directly fundable if portfolio rules permit.",
    "liquid_us_etf": "Liquid U.S.-listed ETF proxy; eligible for ranking subject to pricing and history.",
    "liquid_country_etf": "Liquid country ETF proxy; eligible for ranking subject to pricing and macro fit.",
    "specialist_country_etf": "Specialist country ETF proxy; review liquidity and spread before funding.",
    "local_listing_reference": "Local listing useful for reference only; do not fund without ETF proxy confirmation.",
}

SPECIALIST_PROXIES = {"EZA", "EIDO", "KSA"}
FACTOR_PROXIES = {"RSP", "QUAL", "USMV", "VLUE"}


def proxy_eligibility(exposure: dict[str, Any], currently_held: bool) -> dict[str, str | bool]:
    proxy = str(exposure.get("primary_proxy") or "").upper()
    if currently_held:
        tier = "core_holding"
    elif proxy in FACTOR_PROXIES:
        tier = "liquid_us_etf"
    elif proxy in SPECIALIST_PROXIES:
        tier = "specialist_country_etf"
    elif proxy:
        tier = "liquid_country_etf"
    else:
        tier = "local_listing_reference"
    return {
        "tier": tier,
        "fundable_if_priced": tier != "local_listing_reference",
        "note": PROXY_ELIGIBILITY[tier],
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def latest_path(output_dir: Path, regex: re.Pattern[str], glob_pattern: str) -> Path | None:
    hits: list[tuple[str, int, Path]] = []
    for path in output_dir.glob(glob_pattern):
        match = regex.match(path.name)
        if match:
            hits.append((match.group(1), int(match.group(2) or "0"), path))
    if not hits:
        return None
    hits.sort(key=lambda x: (x[0], x[1]))
    return hits[-1][2]


def report_date_token(output_dir: Path) -> tuple[str, Path]:
    latest_report = latest_path(output_dir, REPORT_RE, "weekly_indices_review_*.md")
    if latest_report is None:
        raise FileNotFoundError("No weekly_indices_review_*.md file found")
    match = REPORT_RE.match(latest_report.name)
    assert match is not None
    return match.group(1), latest_report


def plan_for_token(output_dir: Path, token: str) -> dict[str, Any]:
    exact = output_dir / f"index_recommendation_plan_{token}.json"
    if exact.exists():
        return _read_json(exact)
    latest_plan = latest_path(output_dir, PLAN_RE, "index_recommendation_plan_*.json")
    return _read_json(latest_plan) if latest_plan else {}


def evidence_for_token(output_dir: Path, token: str) -> dict[str, Any]:
    evidence_path = output_dir / "research" / f"index_candidate_evidence_{token}.json"
    return _read_json(evidence_path) if evidence_path.exists() else {}


def regional_group(exposure_id: str) -> str:
    for group, ids in GROUPS.items():
        if exposure_id in ids:
            return group
    return "Other"


def _catalog_by_id() -> dict[str, dict[str, Any]]:
    return {item["exposure_id"]: item for item in ALL_EXPOSURES}


def _candidate_base(exposure: dict[str, Any], held: bool, position: dict[str, Any]) -> dict[str, Any]:
    eligibility = proxy_eligibility(exposure, held)
    return {
        "exposure_id": exposure["exposure_id"],
        "portfolio_sleeve": exposure.get("portfolio_sleeve") or exposure["display_name"],
        "public_index_name": exposure["display_name"],
        "benchmark_symbol": exposure["benchmark_symbol"],
        "benchmark_name": exposure.get("benchmark_name") or exposure["display_name"],
        "primary_proxy": exposure["primary_proxy"],
        "alternative_proxy": exposure.get("alternative_proxy"),
        "regional_group": regional_group(exposure["exposure_id"]),
        "region": exposure.get("region"),
        "style": exposure.get("style"),
        "currently_held": held,
        "weight_pct": position.get("weight_pct"),
        "proxy_eligibility": eligibility,
    }


def fallback_candidates(state: dict[str, Any], plan: dict[str, Any]) -> list[dict[str, Any]]:
    positions = {p.get("exposure_id"): p for p in (state.get("positions") or [])}
    best_new = {item.get("exposure_id"): item for item in (plan.get("best_new_opportunities") or [])}
    strong_challengers = set((plan.get("continuity") or {}).get("strong_challengers_not_published") or [])
    continuity_new = set((plan.get("continuity") or {}).get("new_entries") or [])
    continuity_retained = set((plan.get("continuity") or {}).get("retained_entries") or [])

    candidates: list[dict[str, Any]] = []
    for exposure in ALL_EXPOSURES:
        exposure_id = exposure["exposure_id"]
        group = regional_group(exposure_id)
        score = GROUP_BASE_SCORE.get(group, 3.0)
        held = exposure_id in positions
        if held:
            score += 0.45
        if exposure_id in continuity_new:
            score += 0.20
        if exposure_id in continuity_retained:
            score += 0.15
        if exposure_id in best_new:
            score = max(score, float(best_new[exposure_id].get("score") or score))
        if exposure_id in strong_challengers:
            score += 0.10

        position = positions.get(exposure_id, {})
        candidate = _candidate_base(exposure, held, position)
        candidate.update(
            {
                "score": round(min(score, 4.60), 2),
                "board_score": round(min(score, 4.60), 2),
                "challenger_score": round(min(score - (0.15 if held else 0.0), 4.60), 2),
                "relative_strength_score": None,
                "regime_alignment_score": None,
                "implementation_priority_score": None,
                "diversification_score": None,
                "continuity_bonus": None,
                "fragility_penalty": None,
                "evidence_source": "fallback_regional_base_scores",
                "publish": False,
                "reason_code_if_not_published": "",
            }
        )
        candidates.append(candidate)
    candidates.sort(key=lambda item: (-float(item["board_score"]), -float(item["challenger_score"]), item["public_index_name"]))
    return candidates


def evidence_candidates(state: dict[str, Any], evidence: dict[str, Any]) -> list[dict[str, Any]]:
    positions = {p.get("exposure_id"): p for p in (state.get("positions") or [])}
    rows = evidence.get("rows") or []
    catalog = _catalog_by_id()
    candidates: list[dict[str, Any]] = []
    for row in rows:
        exposure_id = row["exposure_id"]
        exposure = catalog.get(exposure_id, row)
        position = positions.get(exposure_id, {})
        held = bool(row.get("currently_held"))
        board_score = round(float(row.get("board_score") or row.get("final_score") or 0.0), 2)
        challenger_score = round(float(row.get("challenger_score") or board_score), 2)
        candidate = _candidate_base(exposure, held, position)
        candidate.update(
            {
                "score": board_score,
                "board_score": board_score,
                "challenger_score": challenger_score,
                "relative_strength_score": row.get("relative_strength_score"),
                "regime_alignment_score": row.get("regime_alignment_score"),
                "implementation_priority_score": row.get("implementation_priority_score"),
                "diversification_score": row.get("diversification_score"),
                "continuity_bonus": row.get("continuity_bonus"),
                "fragility_penalty": row.get("fragility_penalty"),
                "evidence_notes": row.get("evidence_notes") or {},
                "evidence_source": "candidate_evidence_artifact",
                "publish": False,
                "reason_code_if_not_published": "",
            }
        )
        candidates.append(candidate)
    candidates.sort(key=lambda item: (-float(item["board_score"]), -float(item["challenger_score"]), item["public_index_name"]))
    return candidates


def _group_limit(group: str) -> int:
    if group == "U.S. core leadership":
        return 3
    if group == "U.S. factor / style alternatives":
        return 1
    return 2


def _can_add(candidate: dict[str, Any], selected: list[dict[str, Any]]) -> bool:
    group = str(candidate["regional_group"])
    count = sum(1 for row in selected if row["regional_group"] == group)
    return count < _group_limit(group)


def _replace_for_breadth(selected: list[dict[str, Any]], candidate: dict[str, Any]) -> list[dict[str, Any]]:
    if candidate["regional_group"] in {row["regional_group"] for row in selected}:
        return selected
    replacement_idx = None
    weakest_score = None
    for idx, row in enumerate(selected):
        duplicate_count = sum(1 for item in selected if item["regional_group"] == row["regional_group"])
        if duplicate_count <= 1:
            continue
        score = float(row["board_score"])
        if weakest_score is None or score < weakest_score:
            weakest_score = score
            replacement_idx = idx
    if replacement_idx is not None and float(candidate["board_score"]) >= float(selected[replacement_idx]["board_score"]) - 0.35:
        selected[replacement_idx] = candidate
    return selected


def assign_publish_flags(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []

    held_candidates = [c for c in candidates if c.get("currently_held") and float(c.get("board_score") or 0.0) >= 1.40]
    held_candidates.sort(key=lambda x: (-float(x.get("board_score") or 0.0), x.get("public_index_name") or ""))
    for candidate in held_candidates:
        if len(selected) >= 4:
            break
        if _can_add(candidate, selected):
            selected.append(candidate)

    overall_candidates = sorted(candidates, key=lambda x: (-float(x.get("board_score") or 0.0), -float(x.get("challenger_score") or 0.0), x.get("public_index_name") or ""))
    for candidate in overall_candidates:
        if candidate["exposure_id"] in {row["exposure_id"] for row in selected}:
            continue
        if len(selected) >= 5:
            break
        if _can_add(candidate, selected):
            selected.append(candidate)

    unique_groups = {row["regional_group"] for row in selected}
    if len(unique_groups) < 3:
        challenger_order = sorted(
            [c for c in candidates if not c.get("currently_held")],
            key=lambda x: (-float(x.get("challenger_score") or 0.0), x.get("public_index_name") or ""),
        )
        for candidate in challenger_order:
            if candidate["exposure_id"] in {row["exposure_id"] for row in selected}:
                continue
            selected = _replace_for_breadth(selected, candidate)
            unique_groups = {row["regional_group"] for row in selected}
            if len(unique_groups) >= 3:
                break

    selected_ids = {row["exposure_id"] for row in selected}
    published_challenger_scores = [float(row["challenger_score"]) for row in selected]
    publish_challenger_cutoff = min(published_challenger_scores) if published_challenger_scores else 0.0

    for candidate in candidates:
        candidate["publish"] = candidate["exposure_id"] in selected_ids
        if candidate["publish"]:
            candidate["reason_code_if_not_published"] = ""
            continue
        if candidate.get("currently_held") and float(candidate.get("board_score") or 0.0) >= 1.40:
            candidate["reason_code_if_not_published"] = "held_but_not_board_named"
        elif float(candidate.get("challenger_score") or 0.0) >= publish_challenger_cutoff - 0.20:
            candidate["reason_code_if_not_published"] = "strong_challenger_not_published"
        elif float(candidate.get("relative_strength_score") or 0.0) < 0.80:
            candidate["reason_code_if_not_published"] = "weak_relative_strength"
        elif float(candidate.get("regime_alignment_score") or 0.0) < 0.20:
            candidate["reason_code_if_not_published"] = "fragile_macro_alignment"
        elif float(candidate.get("implementation_priority_score") or 0.0) < 0.15 and float(candidate.get("diversification_score") or 0.0) < 0.12:
            candidate["reason_code_if_not_published"] = "insufficient_immediate_priority"
        else:
            candidate["reason_code_if_not_published"] = "board_capacity"
    return candidates


def build_coverage(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    coverage: list[dict[str, Any]] = []
    for group, ids in GROUPS.items():
        group_candidates = [c for c in candidates if c["exposure_id"] in ids]
        if not group_candidates:
            coverage.append(
                {
                    "group": group,
                    "status": "ruled_out",
                    "reason_if_ruled_out": "no_candidate_available",
                    "strongest_candidate": None,
                    "candidate_count": 0,
                    "eligible_proxy_count": 0,
                }
            )
            continue

        strongest = sorted(
            group_candidates,
            key=lambda x: ((1 if x.get("publish") else 0), float(x.get("board_score") or 0.0), float(x.get("challenger_score") or 0.0)),
            reverse=True,
        )[0]
        status = "considered"
        if strongest["publish"]:
            status = "surfaced"
        elif strongest["reason_code_if_not_published"] == "strong_challenger_not_published":
            status = "near_miss"
        elif float(strongest.get("challenger_score") or 0.0) < 1.50:
            status = "ruled_out"

        eligible_count = sum(1 for c in group_candidates if (c.get("proxy_eligibility") or {}).get("fundable_if_priced"))
        coverage.append(
            {
                "group": group,
                "status": status,
                "reason_if_ruled_out": "score_below_relevance_threshold" if status == "ruled_out" else "",
                "candidate_count": len(group_candidates),
                "eligible_proxy_count": eligible_count,
                "strongest_candidate": {
                    "exposure_id": strongest["exposure_id"],
                    "portfolio_sleeve": strongest.get("portfolio_sleeve"),
                    "public_index_name": strongest["public_index_name"],
                    "benchmark_name": strongest.get("benchmark_name"),
                    "primary_proxy": strongest["primary_proxy"],
                    "score": strongest["score"],
                    "board_score": strongest.get("board_score"),
                    "challenger_score": strongest.get("challenger_score"),
                    "publish": strongest["publish"],
                    "reason_code_if_not_published": strongest["reason_code_if_not_published"],
                    "proxy_eligibility": strongest.get("proxy_eligibility"),
                },
            }
        )
    return coverage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output_indices")
    parser.add_argument("--state-path", default="output_indices/index_portfolio_state.json")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    state_path = Path(args.state_path)
    if not state_path.exists():
        raise FileNotFoundError(f"Missing state file: {state_path}")

    token, latest_report = report_date_token(output_dir)
    state = _read_json(state_path)
    plan = plan_for_token(output_dir, token)
    evidence = evidence_for_token(output_dir, token)

    candidates = evidence_candidates(state, evidence) if evidence else fallback_candidates(state, plan)
    candidates = assign_publish_flags(candidates)
    coverage = build_coverage(candidates)

    ranking_payload = {
        "report_date_token": token,
        "report_file": latest_report.name,
        "requested_close_date": evidence.get("requested_close_date") if evidence else None,
        "evidence_file": f"index_candidate_evidence_{token}.json" if evidence else None,
        "regional_group_status": coverage,
        "scan_summary": {
            "coverage_universe_count": len(candidates),
            "regional_group_count": len(GROUPS),
            "eligible_proxy_count": sum(1 for c in candidates if (c.get("proxy_eligibility") or {}).get("fundable_if_priced")),
            "compact_board_limit": 5,
            "rule": "Broad scan universe first; compact board second. Candidates require proxy eligibility, pricing, regime fit and relative-strength evidence before funding.",
        },
        "candidates": candidates,
    }
    coverage_payload = {
        "report_date_token": token,
        "report_file": latest_report.name,
        "requested_close_date": evidence.get("requested_close_date") if evidence else None,
        "evidence_file": f"index_candidate_evidence_{token}.json" if evidence else None,
        "scan_summary": ranking_payload["scan_summary"],
        "groups": coverage,
    }

    ranking_path = output_dir / f"index_candidate_ranking_{token}.json"
    coverage_path = output_dir / f"index_discovery_coverage_{token}.json"
    _write_json(ranking_path, ranking_payload)
    _write_json(coverage_path, coverage_payload)

    surfaced = sum(1 for row in coverage if row["status"] == "surfaced")
    near_miss = sum(1 for row in coverage if row["status"] == "near_miss")
    evidence_mode = "candidate_evidence_artifact" if evidence else "fallback_regional_base_scores"
    print(
        f"CANDIDATE_ARTIFACTS_OK | report={latest_report.name} | ranking={ranking_path.name} | coverage={coverage_path.name} | "
        f"scan_universe={len(candidates)} | surfaced_groups={surfaced} | near_miss_groups={near_miss} | mode={evidence_mode}"
    )


if __name__ == "__main__":
    main()
