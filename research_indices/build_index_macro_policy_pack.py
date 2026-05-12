from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .common import latest_report_token, resolve_requested_close_date


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def _latest_research_file(output_dir: Path, prefix: str, token: str) -> Path | None:
    exact = output_dir / "research" / f"{prefix}_{token}.json"
    if exact.exists():
        return exact
    hits = sorted((output_dir / "research").glob(f"{prefix}_*.json")) if (output_dir / "research").exists() else []
    return hits[-1] if hits else None


def _pct(value: Any) -> float:
    try:
        return float(value or 0.0) * 100.0
    except (TypeError, ValueError):
        return 0.0


def _series_return(snapshot: dict[str, Any], symbol: str, key: str = "return_20d") -> float:
    return _pct(((snapshot.get("series") or {}).get(symbol) or {}).get(key))


def classify_regime(macro_snapshot: dict[str, Any]) -> tuple[str, float, list[str]]:
    signals = macro_snapshot.get("market_signals", {}) or {}
    suggested = str(macro_snapshot.get("suggested_primary_regime") or "Policy Transition / Mixed Regime")
    qqq_vs_spy = _series_return(macro_snapshot, "QQQ") - _series_return(macro_snapshot, "SPY")
    iwm_vs_spy = _series_return(macro_snapshot, "IWM") - _series_return(macro_snapshot, "SPY")
    uup = _series_return(macro_snapshot, "UUP")
    tlt = _series_return(macro_snapshot, "TLT")
    hyg = _series_return(macro_snapshot, "HYG")

    changes: list[str] = []
    if qqq_vs_spy > 0.75 and iwm_vs_spy < -1.00:
        regime = "Risk-on narrow US mega-cap leadership"
        confidence = 0.72
        changes.append("Nasdaq leadership is stronger than small-cap breadth, so risk appetite remains narrow rather than broad.")
    elif suggested == "Soft Landing" and iwm_vs_spy >= -0.50 and hyg > 0:
        regime = "Risk-on broad participation"
        confidence = 0.68
        changes.append("Credit and breadth are supportive enough to widen the opportunity set beyond U.S. mega-cap leadership.")
    elif uup > 1.25 and signals.get("em_confirmation") == "headwind":
        regime = "USD liquidity squeeze"
        confidence = 0.66
        changes.append("Dollar pressure is a headwind for EM and non-U.S. beta.")
    elif tlt < -1.00 and signals.get("duration_support") == "headwind":
        regime = "Rate-hike repricing / real-rate pressure"
        confidence = 0.64
        changes.append("Duration weakness keeps the bar high for small caps and rate-sensitive exposures.")
    elif suggested == "Slowdown / Defensive":
        regime = "Defensive rotation"
        confidence = 0.65
        changes.append("Risk appetite and breadth are weak enough to prioritize defense and hedge readiness.")
    else:
        regime = "Policy transition / mixed regime"
        confidence = 0.63
        changes.append("No decisive full-regime break; allocation discipline matters more than broad expansion.")

    if qqq_vs_spy > 0.75:
        changes.append("Growth leadership remains visible versus broad U.S. beta.")
    if iwm_vs_spy < -1.00:
        changes.append("Small-cap breadth is still not confirming broad risk-on participation.")
    if uup > 1.25:
        changes.append("Dollar strength remains a constraint for EM and commodity-sensitive non-U.S. exposure.")
    if len(changes) < 3 and hyg > 0:
        changes.append("Credit does not currently signal acute systemic stress.")
    return regime, confidence, changes[:3]


def geopolitical_regime_for_macro(regime: str, uup: float, tlt: float) -> dict[str, Any]:
    if uup > 1.25:
        current = "Elevated USD / policy-friction risk"
        implication = "Keep EM, China, Korea/Taiwan and commodity-sensitive regions on a higher evidence hurdle until USD pressure eases."
        confidence = 0.62
    elif tlt < -1.00:
        current = "Rates and energy-sensitive geopolitical risk"
        implication = "Treat oil, rates and defense/geopolitical shocks as risk filters for small caps, EM and Europe."
        confidence = 0.60
    elif "narrow" in regime.lower():
        current = "Elevated but not portfolio-overriding"
        implication = "Geopolitical risk is a filter, not a standalone allocation driver this week; concentration and breadth remain more important."
        confidence = 0.58
    else:
        current = "Moderate monitoring regime"
        implication = "No geopolitical channel is strong enough to override price, breadth and proxy evidence this week."
        confidence = 0.55
    return {
        "current": current,
        "confidence": confidence,
        "main_channels": ["energy", "defense spending", "China/Taiwan risk", "USD liquidity", "supply-chain concentration"],
        "portfolio_implication": implication,
        "transfer_to_report": True,
    }


def central_banks_for_regime(regime: str) -> dict[str, dict[str, Any]]:
    return {
        "fed": {
            "stance": "restrictive / data-dependent",
            "likely_direction": "hold-to-ease path, but timing remains data-dependent",
            "main_risk": "real-rate repricing pressures small caps, EM and speculative beta",
            "index_implication": "prefer quality and confirmed leadership over weak breadth",
            "transfer_to_report": True,
        },
        "ecb": {
            "stance": "gradual easing bias",
            "likely_direction": "policy support can help Europe only if earnings and price confirmation improve",
            "main_risk": "Europe catch-up fails if global growth or currency support weakens",
            "index_implication": "Europe stays on the board, but not as automatic capital",
            "transfer_to_report": regime in {"Risk-on broad participation", "Policy transition / mixed regime"},
        },
        "boj": {
            "stance": "normalization risk",
            "likely_direction": "yen and yield shifts can affect global liquidity",
            "main_risk": "Japan exposure can be volatile if yen/yield repricing accelerates",
            "index_implication": "Japan requires confirmation, not only structural reform narrative",
            "transfer_to_report": False,
        },
        "boe": {
            "stance": "mixed growth / inflation",
            "likely_direction": "cautious easing bias",
            "main_risk": "UK remains more defensive-yield than growth leadership",
            "index_implication": "UK is a diversification watchlist lane",
            "transfer_to_report": False,
        },
        "pboc": {
            "stance": "targeted support",
            "likely_direction": "stimulus support is possible but confidence-sensitive",
            "main_risk": "China and EM rallies can fail without durable policy credibility",
            "index_implication": "China / EM remain tactical unless price confirmation improves",
            "transfer_to_report": regime in {"China stimulus beta", "USD liquidity squeeze"},
        },
    }


def build_pack(output_dir: Path, token: str, requested_close_date: str) -> dict[str, Any]:
    macro_path = _latest_research_file(output_dir, "index_macro_snapshot", token)
    rs_path = _latest_research_file(output_dir, "index_relative_strength_snapshot", token)
    macro = _read_json(macro_path) if macro_path else {}
    regime, confidence, what_changed = classify_regime(macro)

    qqq_vs_spy = _series_return(macro, "QQQ") - _series_return(macro, "SPY")
    iwm_vs_spy = _series_return(macro, "IWM") - _series_return(macro, "SPY")
    uup = _series_return(macro, "UUP")
    tlt = _series_return(macro, "TLT")
    hyg = _series_return(macro, "HYG")
    geopolitical = geopolitical_regime_for_macro(regime, uup, tlt)

    long_adjustments = {
        "us_tech_leadership": {
            "score_adjustment": 0.12 if qqq_vs_spy > 0 else 0.00,
            "reason": "Nasdaq leadership remains the cleanest long-side index impulse." if qqq_vs_spy > 0 else "Nasdaq leadership is not strong enough for an extra macro boost.",
        },
        "us_small_cap": {
            "score_adjustment": -0.12 if iwm_vs_spy < -1.0 or tlt < -1.0 else 0.04,
            "reason": "Small-cap breadth and real-rate conditions remain insufficient for broad risk expansion." if iwm_vs_spy < -1.0 or tlt < -1.0 else "Small-cap breadth is improving enough to stay under review.",
        },
        "em_broad": {
            "score_adjustment": -0.10 if uup > 1.25 else 0.05,
            "reason": "Dollar pressure keeps EM broad under a higher evidence hurdle." if uup > 1.25 else "A weaker dollar backdrop would improve EM timing.",
        },
        "europe_large_cap": {
            "score_adjustment": 0.05 if regime != "USD liquidity squeeze" else -0.04,
            "reason": "Europe remains a diversification candidate, but price confirmation is still required.",
        },
        "japan_equities": {
            "score_adjustment": 0.05,
            "reason": "Japan remains a valid non-U.S. developed diversification lane, subject to currency/yield volatility.",
        },
        "australia_large_cap": {
            "score_adjustment": -0.03 if uup > 1.25 else 0.03,
            "reason": "Australia is commodity and China-sensitive; require confirmation when USD or China stress rises.",
        },
        "south_korea_large_cap": {
            "score_adjustment": 0.04 if qqq_vs_spy > 0 else -0.02,
            "reason": "Korea adds semiconductor/export-cycle exposure, but needs global tech and currency confirmation.",
        },
        "taiwan_large_cap": {
            "score_adjustment": 0.05 if qqq_vs_spy > 0 else -0.03,
            "reason": "Taiwan is a high-quality semiconductor lane but carries supply-chain and geopolitical concentration risk.",
        },
        "brazil_large_cap": {
            "score_adjustment": -0.04 if uup > 1.25 else 0.02,
            "reason": "Brazil needs commodity support and a friendlier dollar backdrop before promotion.",
        },
        "mexico_large_cap": {
            "score_adjustment": 0.02,
            "reason": "Mexico adds nearshoring exposure, but still requires price confirmation versus broad EM.",
        },
        "indonesia_large_cap": {
            "score_adjustment": -0.02 if uup > 1.25 else 0.02,
            "reason": "Indonesia adds ASEAN domestic-demand beta but remains liquidity and USD-sensitive.",
        },
        "saudi_large_cap": {
            "score_adjustment": 0.02,
            "reason": "Saudi exposure is energy and domestic-reform sensitive; use as a specialist Middle East lane.",
        },
        "us_equal_weight": {
            "score_adjustment": -0.04 if iwm_vs_spy < -1.0 else 0.07,
            "reason": "Equal weight is the cleanest test of U.S. breadth improvement beyond mega-cap concentration.",
        },
        "us_quality_factor": {
            "score_adjustment": 0.05,
            "reason": "Quality can preserve U.S. exposure while reducing weaker balance-sheet beta.",
        },
        "us_min_vol_factor": {
            "score_adjustment": 0.03 if "defensive" in regime.lower() else 0.00,
            "reason": "Minimum volatility becomes more useful if risk appetite deteriorates.",
        },
        "us_value_factor": {
            "score_adjustment": 0.03 if iwm_vs_spy > -0.5 else -0.02,
            "reason": "Value needs evidence of broadening, rates stability and cyclical participation.",
        },
    }

    defensive_adjustments = {
        "RWM": {
            "underlying": "IWM / Russell 2000",
            "readiness": "watchlist" if iwm_vs_spy < -1.0 else "inactive",
            "reason": "Small-cap breadth remains weak versus SPY." if iwm_vs_spy < -1.0 else "Small-cap breadth is not weak enough for an active inverse stance.",
        },
        "EUM": {
            "underlying": "EEM / Emerging Markets",
            "readiness": "watchlist" if uup > 1.25 else "inactive",
            "reason": "Dollar pressure is a headwind for EM." if uup > 1.25 else "Dollar pressure is not strong enough to activate EM inverse readiness.",
        },
        "PSQ": {
            "underlying": "QQQ / Nasdaq 100",
            "readiness": "inactive" if qqq_vs_spy > 0 else "watchlist",
            "reason": "Nasdaq leadership remains intact." if qqq_vs_spy > 0 else "Nasdaq leadership is weakening and requires hedge monitoring.",
        },
    }

    implications = [
        "Do not treat narrow U.S. leadership as full global breadth confirmation.",
        "Keep IWM and EM funding conditional on breadth, dollar and real-rate improvement.",
        "Keep defensive / inverse candidates separate from the long-side opportunity board.",
    ]
    if regime == "Risk-on broad participation":
        implications = [
            "Broader participation allows more capital to be considered outside U.S. mega-cap leadership.",
            "Still require proxy pricing and relative-strength confirmation before funding challengers.",
            "Defensive / inverse readiness can remain secondary unless breadth deteriorates again.",
        ]
    elif regime == "USD liquidity squeeze":
        implications = [
            "Keep EM and China exposure on a tighter evidence leash while the dollar is firm.",
            "EUM-style defensive readiness deserves monitoring but not automatic execution.",
            "U.S. quality and cash discipline remain more important than broad beta expansion.",
        ]

    return {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "report_date": requested_close_date,
        "report_token": token,
        "source_files": {
            "macro_snapshot": str(macro_path) if macro_path else None,
            "relative_strength_snapshot": str(rs_path) if rs_path else None,
        },
        "regime": {
            "current": regime,
            "previous": "Unknown",
            "confidence": confidence,
            "what_changed": what_changed,
            "portfolio_implication": implications[0],
        },
        "geopolitical_regime": geopolitical,
        "central_banks": central_banks_for_regime(regime),
        "macro_signals": {
            "equity_breadth": {"qqq_vs_spy_20d_pct": round(qqq_vs_spy, 2), "iwm_vs_spy_20d_pct": round(iwm_vs_spy, 2)},
            "usd": {"uup_20d_pct": round(uup, 2)},
            "duration": {"tlt_20d_pct": round(tlt, 2)},
            "credit": {"hyg_20d_pct": round(hyg, 2)},
        },
        "region_implications": {
            "US": "Leadership is investable but concentration must be explicit.",
            "US factors": "Equal weight, quality, minimum volatility and value should be used to test breadth and factor rotation without adding new region risk.",
            "Europe": "Diversification candidate; requires price confirmation.",
            "Japan": "Valid developed-market alternative; monitor yen/yield volatility.",
            "Australia": "Commodity, banks and China-sensitive developed-market lane; needs commodity and China confirmation.",
            "Korea / Taiwan": "Semiconductor supply-chain leadership can support the AI/tech regime, but geopolitical and currency risk must be explicit.",
            "Latin America": "Brazil and Mexico deserve scan coverage, but funding requires USD, commodities and domestic policy confirmation.",
            "ASEAN": "Indonesia is a specialist domestic-demand and commodity lane; keep behind liquid core proxies unless signal improves.",
            "Middle East": "Saudi Arabia is an energy/reform specialist lane rather than a broad market replacement.",
            "Emerging Markets": "Higher hurdle when USD pressure is firm.",
        },
        "long_lane_adjustments": long_adjustments,
        "defensive_inverse_adjustments": defensive_adjustments,
        "portfolio_implications": implications,
        "report_digest": {
            "headline": f"{regime}: stay selective and separate long opportunities from defensive / inverse readiness.",
            "top_changes": what_changed[:3],
            "decision_implications": implications[:3],
            "central_bank_focus": "Fed real-rate risk remains the key policy filter for small caps, EM and speculative beta.",
            "geopolitical_focus": geopolitical["portfolio_implication"],
            "risk_watch": "A stronger USD or renewed rate repricing would raise the hurdle for EM, small caps and non-U.S. cyclicals.",
        },
        "report_transfer": {
            "max_what_changed_bullets": 3,
            "max_portfolio_implications": 3,
            "max_central_bank_or_policy_points": 2,
            "style_rule": "Transfer only decision-relevant macro information; do not dump the pack into the report.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output_indices")
    parser.add_argument("--token", default=None)
    parser.add_argument("--requested-close-date", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    token = args.token or latest_report_token(output_dir)
    requested_close_date = args.requested_close_date or resolve_requested_close_date(output_dir)
    pack = build_pack(output_dir, token, requested_close_date)

    macro_dir = output_dir / "macro"
    dated_path = macro_dir / f"index_macro_policy_pack_{token}.json"
    latest_path = macro_dir / "latest.json"
    _write_json(dated_path, pack)
    _write_json(latest_path, pack)

    print(
        "INDEX_MACRO_POLICY_PACK_OK | "
        f"token={token} | requested_close={requested_close_date} | regime={pack['regime']['current']} | output={dated_path.name}"
    )


if __name__ == "__main__":
    main()
