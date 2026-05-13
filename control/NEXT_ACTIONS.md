# Weekly Index OS — Next Actions

## Status legend
- `[USER]` = manual user action
- `[ASSISTANT]` = can be done directly in repo/chat
- `[JOINT]` = assistant prepares, user wires providers, secrets, or external systems

---

## Phase 1 — keep the working environment disciplined

### 1. Keep using the control-layer read order
- Owner: `[JOINT]`
- Action: every meaningful Weekly Index architecture, debugging, prompt, state, workflow, delivery, or report-quality session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer rediscover the architecture.

### 2. Keep GitHub as source of truth
- Owner: `[JOINT]`
- Action: read changing repo files live from GitHub and do not rely on stale copies.
- Done when: prompt, state, workflow, and output changes are all traceable in GitHub.

---

## Phase 2 — validate ETF-derived capital discipline in the next live Index report

### 3. Validate recommendation scorecard derivation
- Owner: `[ASSISTANT]`
- Source files:
  - `index.txt`
  - `control/INDEX_CAPITAL_REUNDERWRITING_RULES.md`
  - `tools/write_index_recommendation_scorecard.py`
- Action:
  - confirm `tools/write_index_recommendation_scorecard.py --check-only` passes before send
  - confirm `output_indices/index_recommendation_scorecard.csv` refreshes after successful publication
  - inspect whether discipline flags are useful and not noisy
- Done when: the scorecard is stable across a live run.

### 4. Force current weak-point reviews
- Owner: `[ASSISTANT]`
- Action: in the next report explicitly review:
  - SPY / QQQ factor overlap and U.S. mega-cap concentration
  - IWM breadth validity and RWM defensive comparison
  - EEM dollar/EM validity and EUM defensive comparison
  - cash reserve versus actionable challengers
  - whether Japan, Europe, UK, Switzerland, Canada, Australia, Greater China, India, Korea/Taiwan, LatAm, ASEAN, Middle East, or EM broad deserve funded capital
- Done when: no weak or replaceable holding remains vague.

### 5. Validate short opportunities radar in Section 11
- Owner: `[ASSISTANT]`
- Action:
  - confirm Section 11 contains `Long-side Opportunities`
  - confirm Section 11 contains `Alternative Duel Table`
  - confirm Section 11 contains `Best Defensive / Inverse Opportunities`
  - confirm inverse candidates are separated from the long board
  - confirm triggers and invalidations are present
- Done when: the short radar is visible, decision-useful, and not confused with base-case allocation.

---

## Phase 3 — send-path and stale-data hardening

### 6. Confirm production workflow trigger behavior
- Owner: `[JOINT]`
- Action:
  - confirm GitHub Actions triggers on canonical report pushes and run-queue request files
  - confirm logs produce visible render/send/manifest evidence
  - avoid claiming delivery success without a real receipt
- Done when: delivery status can be verified reliably.

### 7. Validate pricing and NAV reconciliation
- Owner: `[ASSISTANT]`
- Action:
  - confirm pricing pass uses latest completed U.S. regular-session close
  - confirm Section 7 latest row equals Section 15 total portfolio value
  - confirm `index_portfolio_state.json` matches report Section 15
  - confirm pricing audit is persisted under `output_indices/pricing/`
  - confirm `tools/validate_index_state_consistency_contract.py` blocks stale NAV/pricing-date leakage in executive sections
- Done when: stale prices cannot silently flatten, distort, or misstate the report.

### 8. Confirm scorecard validation blocks bad sends
- Owner: `[ASSISTANT]`
- Action:
  - intentionally review the workflow ordering
  - ensure scorecard derivation runs before render/email
  - ensure scorecard is written and committed back only after successful send
- Done when: incomplete capital-discipline reports cannot be sent unnoticed.

### 9. Validate layered close-price discovery model
- Owner: `[ASSISTANT]` + `[JOINT]` if provider secrets are required
- Current status: implemented as `layered_close_discovery_v1` in the Weekly Index pricing subsystem; needs validation in the next live run.
- Implemented behavior:
  - source fallback order: Yahoo history → Twelve Data → FMP → Alpha Vantage → carried-forward prior valid close
  - separate benchmark close and tradable-proxy close retrieval
  - provider/source/status diagnostics persisted in `output_indices/pricing/index_price_audit_*.json`
  - per-holding performance metrics persisted into `output_indices/index_portfolio_state.json`
  - pricing contract validates layered model, provider order, price-source diagnostics, and performance metric presence
- Action:
  - run a fresh report and inspect pricing audit source distribution
  - verify Twelve Data/FMP/Alpha Vantage fallbacks are used when Yahoo fails or is incomplete
  - confirm hard failure for missing proxy closes on funded positions
  - confirm benchmark gaps are visible without corrupting valuation authority
- Done when: Weekly Index pricing is operationally as robust as Weekly ETF while preserving benchmark-vs-proxy distinctions.

---

## Phase 4 — make the report consume the new artifacts correctly

### 10. Validate artifact-driven Section 11
- Owner: `[ASSISTANT]`
- Action:
  - confirm `research_indices/build_index_alternative_duels.py` creates usable direct-duel rows
  - confirm `research_indices/build_index_short_radar.py` creates decision-grade inverse/defensive rows
  - confirm `pricing_indices/assemble_report_sections.py` renders Section 11 from those artifacts
  - confirm old hand-written short radar text no longer appears
- Done when: Section 11 is artifact-driven and decision-grade.

### 11. Tighten compactness and client-facing wording
- Owner: `[ASSISTANT]`
- Action:
  - confirm `tools/validate_index_compactness_contract.py` blocks raw artifact terms and process terms
  - remove `TBD`, `live repo state`, `pricing/ranking rebuild`, and workflow-process language from the client report
  - preserve compact report style; do not add long macro dumps
- Done when: report reads like a client report, not a workflow log.

### 12. Fix remaining render polish issues
- Owner: `[ASSISTANT]`
- Action:
  - fix missing spaces around linked tickers such as `IWMversus`, `EWJand`, `SPYand`, `QQQtogether`
  - remove orphan bullet artifacts at the bottom of pages
  - avoid repeated headers after the equity-curve image
  - reduce equity-curve x-axis label overlap
- Done when: PDF rendering looks premium and does not expose markdown/render artifacts.

### 13. Validate ETF-style tradable proxy performance table
- Owner: `[ASSISTANT]`
- Current status: implemented in the composer as `Tradable Proxy Performance` inside Section 15.
- Action:
  - confirm table appears in the next report
  - confirm each funded proxy has 1w, 1m, 3m, since-entry, P/L EUR, and contribution fields
  - confirm values come from `index_portfolio_state.json` performance metrics
  - confirm `tools/validate_index_state_consistency_contract.py` blocks missing performance rows or missing required columns
- Done when: Weekly Index has ETF-style per-position performance visibility.

---

## Phase 5 — improve explicit Index state quality

### 14. Improve recommendation scorecard quality
- Owner: `[ASSISTANT]`
- Action:
  - add real 1-month and 3-month relative-strength values when reliable price history is available
  - improve best-alternative scoring
  - improve cash classification extraction
  - improve consecutive-week replaceable history
- Done when: scorecard becomes less heuristic and more data-backed.

### 15. Move Index state beyond report-derived state over time
- Owner: `[ASSISTANT]`
- Action:
  - validate the pricing subsystem in real runs
  - add more valuation authority from machine-readable pricing outputs
  - reduce dependence on report-derived state where safe
- Done when: explicit state is less dependent on rendered report parsing.

### 16. Improve factor and breadth model
- Owner: `[ASSISTANT]`
- Action:
  - make U.S. equity beta, mega-cap growth, small-cap financing sensitivity, non-U.S. exposure, EM/dollar sensitivity, and defensive/inverse readiness more data-backed
  - preserve report compactness
- Done when: concentration warnings are useful and not just hard-coded labels.

---

## Phase 6 — keep AEX options preserved but parked

### 17. Do not delete the AEX track
- Owner: `[JOINT]`
- Goal:
  - preserve files
  - preserve workflows
  - avoid mixing product logic
- Done when: the repo can support both tracks cleanly without ambiguity.

---

## Current checkpoint

**Weekly Index Review now has the key ETF lessons ported: pricing-first workflow, breadth discipline, short-opportunity radar, macro-policy pack, runtime state artifact, state-consistency validation, compactness validation, alternative-duel artifacts, capital re-underwriting rules, ETF-style tradable proxy performance table, and a first implementation of layered close-price discovery. The next priority is to validate these in a fresh run and inspect the pricing audit, Section 15 performance table, render quality, and delivery manifest.**
