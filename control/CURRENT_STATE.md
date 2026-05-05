# Weekly Index OS — Current State

## Snapshot date
2026-05-05

## What this repository currently is

This repository is now a production-style Weekly Indices Review system with:

- `index.txt` as the production runtime prompt
- `control/INDEX_CAPITAL_REUNDERWRITING_RULES.md` as the ETF-derived index-native capital discipline addendum
- `index-pro.txt` as the premium editorial layer
- `send_index_report.py` / `send_index_report_tv.py` as the delivery and rendering layer
- `.github/workflows/send-weekly-indices-report.yml` as the push-triggered production send workflow
- a pricing subsystem in `pricing_indices/`
- a research subsystem in `research_indices/`
- archived reports in `output_indices/`
- pricing audits in `output_indices/pricing/`
- candidate ranking and discovery coverage artifacts
- explicit index state files:
  - `output_indices/index_portfolio_state.json`
  - `output_indices/index_valuation_history.csv`
  - `output_indices/index_recommendation_scorecard.csv`
- scorecard writer:
  - `tools/write_index_recommendation_scorecard.py`

The AEX options track remains preserved but parked.

## What changed in this step

This update ports the most important lessons from the mature Weekly ETF Review system into the Weekly Index Review product:

- capital re-underwriting discipline
- fresh cash tests
- thesis versus implementation split
- direct alternative-duel requirement for weak or replaceable holdings
- factor-overlap and breadth-concentration checks
- defensive / inverse hedge readiness checks
- cash policy checks
- action-clock / inertia checks
- machine-readable recommendation scorecard memory
- send-path scorecard derivation validation before render and email
- persisted scorecard commit-back after successful delivery

## Why this matters

The Weekly Index Review had already gained pricing, research, breadth, and short-radar layers, but it still lacked the mature ETF discipline that prevents vague `Hold` language from becoming inertia.

This upgrade makes index holdings harder to hide behind:

- weak holdings must be re-underwritten
- replaceable holdings carry a timer and named alternatives
- U.S. concentration must be called out as concentration, not diversification
- small-cap and EM sleeves must justify their role when breadth or dollar pressure weakens
- cash must be classified as reserve, residual, risk reserve, or deployment candidate
- defensive / inverse opportunities remain separated from long-side opportunities
- the scorecard preserves this discipline across runs

## Current strengths

- Strong executive look and feel in the Weekly Index report family.
- Pricing-first workflow exists and fetches fresh proxy/benchmark closes where available.
- Full-universe breadth visibility exists, including Europe, UK, Switzerland, Japan, Canada, Australia, Greater China, India, and EM broad.
- Section 11 includes long-side opportunities and defensive / inverse short opportunities radar.
- Report composition uses artifact-driven Section 4, 7, 11, 15, and 16 replacement.
- Report-vs-ranking and pricing/NAV reconciliation validation exists.
- Delivery workflow validates scorecard derivation before render/send.
- `output_indices/index_recommendation_scorecard.csv` is now the explicit recommendation discipline memory.

## Current weaknesses

### 1. Recommendation scorecard is report-derived
The scorecard currently derives from the canonical Weekly Index report. This is useful state memory, but not yet an independent implementation engine.

### 2. Alternative duel scoring is still partly heuristic
The scorecard stores named alternatives and required next action, but true 1-month / 3-month relative-strength duel values still need deeper machine-readable price history.

### 3. Factor exposure is rule-derived, not lookthrough-derived
The current factor-overlap and breadth-concentration flags are deterministic and useful, but still approximate.

### 4. Control files still need continued cleanup over time
Some historical language from the original AEX/daily-index transition may remain in older docs, but the current canonical source of truth now reflects Weekly Index Review as the active product.

### 5. Delivery status must still be verified from workflow logs or manifest
Do not claim render or email success without actual workflow evidence.

## Immediate priorities

### Priority A — validate scorecard derivation on the next live report
Confirm that:
- `tools/write_index_recommendation_scorecard.py --check-only` passes before send
- `output_indices/index_recommendation_scorecard.csv` refreshes after report publication
- flagged holdings are sensible and not noisy

### Priority B — force decisions on weak or replaceable index sleeves
The next report should explicitly review:
- SPY / QQQ factor overlap and U.S. mega-cap concentration
- IWM breadth validity and RWM defensive comparison
- EEM dollar/EM validity and EUM defensive comparison
- cash policy versus actionable challengers
- whether Europe, Japan, UK, Switzerland, Canada, Australia, Greater China, India, or EM broad deserve more capital

### Priority C — improve scorecard quality over time
Future enhancements:
- add real 1-month and 3-month relative-strength duel values
- add better cash classification extraction
- add more robust factor exposure model
- add explicit consecutive-week replaceable history across reports

### Priority D — keep ETF lessons index-native
Do not blindly copy ETF tickers, ETF state assumptions, or ETF-specific weak-point names. Apply the same discipline to index exposures, benchmark/proxy rules, and short/inverse radar.

## Current status label

**Weekly Index Review now has the key ETF lessons: pricing-first workflow, breadth discipline, short-opportunity radar, state artifact persistence, and a capital re-underwriting scorecard layer. The next live run should validate that weak, concentrated, or replaceable positions can no longer hide behind vague Hold language without named alternatives, triggers, or override reasons.**
