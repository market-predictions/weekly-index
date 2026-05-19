# Weekly Index OS — System Index

This file is the **first entry point** for meaningful work on `market-predictions/weekly-index`.

## Purpose
This repository contains two product tracks:

1. **Weekly Indices Review** — the primary active report product for a model portfolio of stock-index exposures with recommendations, continuity, valuation tracking, delivery, breadth discipline, short-opportunity radar, capital re-underwriting, and bilingual EN/NL output workstream.
2. **AEX Weekly Options** — a parked but preserved options-native track for structured AEX option analysis, machine trade plans, and later possible reuse.

The architecture must keep four layers separate:
- decision framework
- input / state contract
- output contract
- operational runbook

Do not collapse those four layers back into one opaque prompt.

---

## Canonical control files
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`
- `control/PROJECT_BOOTSTRAP.md`
- `control/CHATGPT_PROJECT_INSTRUCTIONS.md`
- `control/OPTIONAL_CUSTOM_GPT_SPEC.md`
- `control/INDICES_REVIEW_ARCHITECTURE.md`
- `control/INDEX_CAPITAL_REUNDERWRITING_RULES.md`
- `control/BILINGUAL_WEEKLY_INDEX_ARCHITECTURE.md`
- `control/NL_TERMINOLOGY.md`
- `control/BILINGUAL_OUTPUT_RULES.md`
- `changelog.md`

---

## Canonical execution files

### Weekly Indices Review — primary active track
- `index.txt`
- `index-pro.txt`
- `prompts/weekly_indices/01_DECISION_FRAMEWORK.md`
- `prompts/weekly_indices/02_INPUT_STATE_CONTRACT.md`
- `prompts/weekly_indices/03_OUTPUT_CONTRACT.md`
- `prompts/weekly_indices/04_OPERATIONAL_RUNBOOK.md`
- `pricing_indices/`
- `research_indices/`
- `send_index_report.py`
- `send_index_report_tv.py`
- `.github/workflows/send-weekly-indices-report.yml`
- `tools/write_index_recommendation_scorecard.py`
- `output_indices/`

### AEX Weekly Options — parked but preserved track
- `prompts/aex_weekly_options/01_DECISION_FRAMEWORK.md`
- `prompts/aex_weekly_options/02_INPUT_STATE_CONTRACT.md`
- `prompts/aex_weekly_options/03_OUTPUT_CONTRACT.md`
- `prompts/aex_weekly_options/04_OPERATIONAL_RUNBOOK.md`
- `build_aex_primary_technical_snapshot.py`
- `build_aex_cross_market_confirmation.py`
- `build_aex_macro_snapshot.py`
- `build_aex_option_surface_snapshot.py`
- `run_aex_snapshot_suite.py`
- `build_aex_structure_candidates.py`
- `refresh_aex_portfolio_and_risk_state.py`
- `generate_weekly_aex_option_review.py`
- `validate_aex_trade_plan.py`
- `send_aex_options_report.py`
- `.github/workflows/refresh-aex-snapshots.yml`
- `.github/workflows/build-weekly-aex-review.yml`
- `.github/workflows/validate-aex-trade-plan.yml`
- `.github/workflows/send-weekly-aex-options.yml`
- `output_aex/`

---

## Operating model

Read the repository in four layers.

### 1. Decision framework
What the Weekly Indices Review is trying to decide:
- macro regime classification
- portfolio changes
- opportunity-board ranking
- short-opportunity / inverse-radar readiness
- capital re-underwriting of every funded exposure
- portfolio evolution through time

### 2. Input / state contract
Where authoritative facts come from, in what order, and how conflicts are resolved:
- requested close date and report token
- benchmark index closes for analysis
- tradable proxy closes for implemented valuation
- portfolio state files
- valuation history
- recommendation plan
- pricing audits
- discovery/ranking artifacts
- recommendation scorecard memory
- continuity memory

### 3. Output contract
How the final report must be structured and rendered.

The Weekly Indices Review should feel comparable to ETF Review:
- executive
- premium
- compact
- decision-useful
- continuity-aware
- operationally auditable
- explicit about long opportunities versus defensive / inverse opportunities
- bilingual-ready without changing the investment model

### 4. Operational runbook
How the review is executed:
- control-layer read order
- pricing pass
- research snapshots
- candidate ranking and discovery coverage
- report section assembly
- capital re-underwriting scorecard validation
- report generation
- GitHub write
- render / PDF
- email delivery
- manifest / receipt
- state/artifact commit-back
- changelog update for meaningful codebase changes

---

## Session start rule
For architecture work, debugging, workflow changes, state-authority work, bilingual work, or report redesign, read in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. only then the minimum relevant execution file(s)

For bilingual work, also read:

5. `control/BILINGUAL_WEEKLY_INDEX_ARCHITECTURE.md`
6. `control/NL_TERMINOLOGY.md`
7. `control/BILINGUAL_OUTPUT_RULES.md`

---

## Non-negotiable discipline
- Do not replace the repo with a blind ETF clone.
- Do not weaken the four-layer architecture.
- Do not delete the AEX options track; preserve it but park it.
- Do not treat benchmark-index closes and tradable-proxy closes as interchangeable.
- Do not claim delivery succeeded without a manifest or receipt.
- Do not let the report become a sprawling macro dump; it must remain compact and premium.
- Do not let the production workflow send mail on non-report code changes.
- Do not allow weak or replaceable holdings to remain indefinite unqualified Holds.
- Do not mix defensive / inverse tools into the long-side opportunity board.
- Do not let the Dutch report run a second investment model or diverge numerically from English.
- Do not make meaningful repo changes without updating `changelog.md`.

---

## Current direction of travel
The target architecture is:

- `weekly-index` remains the dedicated host repo for Weekly Indices Review
- **Weekly Indices Review** is the primary active report product
- **AEX Weekly Options** remains parked but preserved
- `index.txt` is the production runtime prompt
- `control/INDEX_CAPITAL_REUNDERWRITING_RULES.md` is the capital-discipline addendum
- `index-pro.txt` is the premium editorial layer
- `send_index_report.py` / `send_index_report_tv.py` plus GitHub Actions are the delivery layer
- `output_indices/` is the canonical output/state path
- benchmark index data drives analysis
- tradable proxy data drives implemented model-portfolio valuation
- `output_indices/index_recommendation_scorecard.csv` is the machine-readable recommendation discipline memory
- Dutch output must be a localized companion view over the same state, token, pricing and decisions
