# Weekly Index OS — Changelog

This file records meaningful codebase, workflow, rendering, state-contract, and control-layer changes for `market-predictions/weekly-index`.

## Logging rule

For every meaningful future repository change, add a dated entry here with:

- what changed
- why it changed
- affected files
- validation / run evidence when available

Tiny typo-only edits do not need a full entry unless they affect output quality, workflow behavior, or client-facing delivery.

---

## 2026-05-19 — Add changelog discipline

### What changed
- Added this root-level `changelog.md` as the canonical change log for meaningful codebase changes.
- Future architecture, workflow, prompt, renderer, pricing, validation, and report-output changes must be logged here.

### Why
The Weekly Index system is now production-like enough that relying only on Git commits and chat memory is not sufficient. A human-readable changelog makes future debugging, handovers, and architecture reviews easier.

### Affected files
- `changelog.md`

### Validation / evidence
- Repo change only; no report run required.

---

## 2026-05-19 — Freeze current English Weekly Index production baseline

### What changed
- Confirmed May 18 pricing freshness and report-token discipline for `weekly_indices_review_260518.md`.
- Confirmed Section 7 owns the equity curve and Tradable Proxy Performance table.
- Confirmed Section 15 is holdings/cash only.
- Confirmed Investor Report / Analyst Report visual split, with the Analyst Report using the petrol-teal identity.
- Confirmed table tickers are TradingView-linked.
- Confirmed native list markers are inlined to avoid PDF ghost bullets.
- Confirmed equity-curve chart x-axis labels use print-safe spacing.

### Why
These are now stable output-contract and operational-baseline decisions. They should not be treated as open issues when starting the bilingual Weekly Index model.

### Affected files / areas
- `.github/workflows/send-weekly-indices-report.yml`
- `pricing_indices/assemble_report_sections.py`
- `pricing_indices/compose_final_report.py`
- `pricing_indices/performance_table.py`
- `send_index_report_tv_analyst_distinct.py`
- `send_index_report_equity_chart_polish.py`
- `tools/validate_index_report_token_for_close.py`
- `tools/validate_index_ticker_links.py`
- `tools/validate_index_render_polish.py`
- `tools/write_weekly_indices_run_manifest_for_report.py`
- `output_indices/weekly_indices_review_260518.md`
- `output_indices/run_manifests/`

### Validation / evidence
- Fresh run succeeded with report token `260518`, requested close date `2026-05-18`, and portfolio value EUR `111,116.08`.
- Latest successful manifest commit referenced workflow success for `output_indices/weekly_indices_review_260518.md`.

---

## 2026-05-19 — Freeze control layer and add bilingual architecture design

### What changed
- Updated `control/CURRENT_STATE.md` to describe the validated English Weekly Index baseline.
- Updated `control/NEXT_ACTIONS.md` to make bilingual Weekly Index output the next active workstream.
- Updated `control/DECISION_LOG.md` with stable baseline decisions.
- Added `control/BILINGUAL_WEEKLY_INDEX_ARCHITECTURE.md` before touching bilingual implementation code.

### Why
The repo needed a clean control-layer checkpoint before starting bilingual output. The Dutch report must be a language/rendering layer over the same state and numbers, not a second investment model.

### Affected files
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`
- `control/BILINGUAL_WEEKLY_INDEX_ARCHITECTURE.md`
- `changelog.md`

### Validation / evidence
- Control-layer and architecture documentation only; no report run required.
