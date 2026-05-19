# Weekly Index OS — Next Actions

## Status legend
- `[USER]` = manual user action
- `[ASSISTANT]` = can be done directly in repo/chat
- `[JOINT]` = assistant prepares, user wires providers, secrets, or external systems

---

## Phase 1 — preserve operating discipline

### 1. Keep using the control-layer read order
- Owner: `[JOINT]`
- Action: every meaningful Weekly Index architecture, debugging, prompt, state, workflow, delivery, or report-quality session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions do not rediscover or contradict the architecture.

### 2. Keep GitHub and changelog as source of truth
- Owner: `[JOINT]`
- Action:
  - read changing repo files live from GitHub
  - update `changelog.md` for meaningful codebase/workflow/rendering/control-layer changes
  - update control files when a durable baseline decision changes
- Done when: prompt, state, workflow, and output changes are traceable in GitHub and the changelog.

---

## Phase 2 — start bilingual Weekly Index model

### 3. Design bilingual architecture before implementation
- Owner: `[ASSISTANT]`
- Action: create a bilingual design that keeps these layers separate:
  - decision framework
  - input/state contract
  - output contract
  - operational runbook
- Required principle: the Dutch report must consume the same machine state and pricing artifacts as the English report. It must not run a separate investment model.
- Done when: the bilingual architecture is documented before code changes.

### 4. Add Dutch terminology and language rules
- Owner: `[ASSISTANT]`
- Action: create Dutch terminology controls for recurring finance/reporting terms.
- Required checks:
  - no English weekday/month leakage in Dutch output
  - no awkward literal translations
  - consistent terms for Investor Report, Analyst Report, regime, re-underwriting, defensive/inverse tools, contribution, valuation, cash and holdings
- Done when: a Dutch terminology control file exists and can be validated.

### 5. Add Dutch report generation path
- Owner: `[ASSISTANT]`
- Action: generate a Dutch companion report from the same canonical English/state artifacts.
- Required behavior:
  - same pricing basis
  - same portfolio value
  - same positions
  - same section order
  - same Investor/Analyst split
  - same Tradable Proxy Performance placement after the equity curve
  - same Section 15 holdings/cash-only contract
- Done when: EN and NL reports are generated together from one state.

### 6. Add parity validators
- Owner: `[ASSISTANT]`
- Action: add validators for:
  - numeric parity between EN and NL reports
  - section parity between EN and NL reports
  - Dutch date localization
  - required Dutch terminology
  - no stale report-token mismatch
- Done when: NL cannot be sent if it diverges numerically from EN.

### 7. Add bilingual delivery path
- Owner: `[ASSISTANT]`
- Action: extend delivery so both English and Dutch outputs are rendered and attached/sent together.
- Required behavior:
  - do not claim delivery success without manifest/receipt evidence
  - manifest must identify both EN and NL assets
  - failure in either language should block the bilingual send until resolved
- Done when: a fresh bilingual run produces validated EN + NL PDFs.

---

## Phase 3 — preserve current English baseline

### 8. Keep current English report validators active
- Owner: `[ASSISTANT]`
- Action: do not weaken validators for:
  - requested-close token discipline
  - pricing/NAV reconciliation
  - Section 7 performance-table placement
  - Section 15 holdings/cash-only contract
  - Analyst visual distinction
  - ticker links
  - render polish / inline list markers
  - equity chart embedding
- Done when: bilingual work does not regress the current English baseline.

### 9. Keep short radar and long board separated
- Owner: `[ASSISTANT]`
- Action:
  - confirm Section 11 contains long-side opportunities
  - confirm defensive / inverse opportunities remain separated from the long board
  - confirm triggers and invalidations are present
- Done when: inverse tools never appear as base-case long allocation.

### 10. Keep pricing and token freshness strict
- Owner: `[ASSISTANT]`
- Action:
  - requested close date must resolve before pricing
  - report token must match requested close date
  - state, report, candidate artifacts and manifest must use the same token
- Done when: stale-price or stale-token reports cannot be delivered.

---

## Phase 4 — future model quality improvements after bilingual baseline

### 11. Improve recommendation scorecard quality
- Owner: `[ASSISTANT]`
- Action:
  - add real 1-month and 3-month relative-strength values when reliable price history is available
  - improve best-alternative scoring
  - improve cash classification extraction
  - improve consecutive-week replaceable history
- Done when: scorecard becomes less heuristic and more data-backed.

### 12. Improve factor and breadth model
- Owner: `[ASSISTANT]`
- Action:
  - make U.S. equity beta, mega-cap growth, small-cap financing sensitivity, non-U.S. exposure, EM/dollar sensitivity, and defensive/inverse readiness more data-backed
  - preserve report compactness
- Done when: concentration warnings are useful and not just hard-coded labels.

### 13. Reduce report-derived state over time
- Owner: `[ASSISTANT]`
- Action:
  - move more authority into machine-readable pricing/state artifacts
  - reduce dependence on rendered report parsing where safe
- Done when: explicit state is less dependent on final report text.

---

## Phase 5 — keep AEX options preserved but parked

### 14. Do not delete the AEX track
- Owner: `[JOINT]`
- Goal:
  - preserve files
  - preserve workflows
  - avoid mixing product logic
- Done when: the repo can support both tracks cleanly without ambiguity.

---

## Current checkpoint

**English Weekly Index Review baseline is frozen and validated. The next active workstream is bilingual Weekly Index output, beginning with architecture and terminology controls before implementation.**
