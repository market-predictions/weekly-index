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
  - whether Japan, Europe, UK, Switzerland, Canada, Australia, Greater China, India, or EM broad deserve funded capital
- Done when: no weak or replaceable holding remains vague.

### 5. Validate short opportunities radar in Section 11
- Owner: `[ASSISTANT]`
- Action:
  - confirm Section 11 contains `Long-side Opportunities`
  - confirm Section 11 contains `Best Defensive / Inverse Opportunities`
  - confirm inverse candidates are separated from the long board
  - confirm triggers and invalidations are present
- Done when: the short radar is visible, decision-useful, and not confused with base-case allocation.

---

## Phase 3 — send-path and stale-data hardening

### 6. Confirm production workflow trigger behavior
- Owner: `[JOINT]`
- Action:
  - confirm GitHub Actions triggers on canonical report pushes
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
- Done when: stale prices cannot silently flatten, distort, or misstate the report.

### 8. Confirm scorecard validation blocks bad sends
- Owner: `[ASSISTANT]`
- Action:
  - intentionally review the workflow ordering
  - ensure scorecard derivation runs before render/email
  - ensure scorecard is written and committed back only after successful send
- Done when: incomplete capital-discipline reports cannot be sent unnoticed.

---

## Phase 4 — improve explicit Index state quality

### 9. Improve recommendation scorecard quality
- Owner: `[ASSISTANT]`
- Action:
  - add real 1-month and 3-month relative-strength values when reliable price history is available
  - improve best-alternative scoring
  - improve cash classification extraction
  - improve consecutive-week replaceable history
- Done when: scorecard becomes less heuristic and more data-backed.

### 10. Move Index state beyond report-derived state over time
- Owner: `[ASSISTANT]`
- Action:
  - validate the pricing subsystem in real runs
  - add more valuation authority from machine-readable pricing outputs
  - reduce dependence on report-derived state where safe
- Done when: explicit state is less dependent on rendered report parsing.

### 11. Improve factor and breadth model
- Owner: `[ASSISTANT]`
- Action:
  - make U.S. equity beta, mega-cap growth, small-cap financing sensitivity, non-U.S. exposure, EM/dollar sensitivity, and defensive/inverse readiness more data-backed
  - preserve report compactness
- Done when: concentration warnings are useful and not just hard-coded labels.

---

## Phase 5 — keep AEX options preserved but parked

### 12. Do not delete the AEX track
- Owner: `[JOINT]`
- Goal:
  - preserve files
  - preserve workflows
  - avoid mixing product logic
- Done when: the repo can support both tracks cleanly without ambiguity.

---

## Current checkpoint

**Weekly Index Review now has the key ETF lessons ported: pricing-first workflow, breadth discipline, short-opportunity radar, state artifact persistence, capital re-underwriting rules, and a recommendation scorecard memory layer. The next priority is to validate these rules in the next live report and ensure weak or replaceable positions produce explicit actions, alternatives, triggers, or override reasons.**
