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

---

## 2026-05-19 — Add Dutch terminology and bilingual output rules

### What changed
- Added Dutch terminology controls for the Weekly Index report.
- Added bilingual output rules covering file naming, structure parity, numeric parity, date localization, terminology authority, layout parity, validation requirements, and delivery expectations.
- Updated `control/SYSTEM_INDEX.md` so bilingual controls are part of the canonical read set.

### Why
Bilingual implementation needs stable terminology and output-contract rules before code generation starts. The Dutch report must use the same state, token, pricing and investment decisions as the English report while avoiding awkward literal translations and English date leakage.

### Affected files
- `control/NL_TERMINOLOGY.md`
- `control/BILINGUAL_OUTPUT_RULES.md`
- `control/SYSTEM_INDEX.md`
- `changelog.md`

### Validation / evidence
- Control-layer documentation only; no report run required.

---

## 2026-05-19 — Add Dutch markdown draft generation path without email delivery

### What changed
- Added a first deterministic Dutch markdown generator for Weekly Index reports.
- Added Dutch language-contract validation.
- Added EN/NL section-parity validation.
- Added EN/NL numeric-parity validation.
- Added a manual NL draft workflow that generates and commits Dutch markdown only; it does not render/send email.
- Restricted the production English send workflow trigger to run-queue requests only, so committing Dutch draft markdown cannot accidentally trigger report delivery.

### Why
The bilingual rollout should first prove markdown generation and parity before introducing Dutch PDF rendering or bilingual email delivery. The Dutch report must remain a localized companion view over the same English/state artifacts.

### Affected files
- `tools/generate_index_nl_report.py`
- `tools/validate_index_nl_language_contract.py`
- `tools/validate_index_bilingual_section_parity.py`
- `tools/validate_index_bilingual_numeric_parity.py`
- `.github/workflows/build-weekly-index-nl-draft.yml`
- `.github/workflows/send-weekly-indices-report.yml`
- `changelog.md`

### Validation / evidence
- Code and workflow path added. Next validation step is to run the manual `Build Weekly Index NL draft` workflow with report token `260518` and inspect the committed Dutch markdown draft.

---

## 2026-05-19 — Fix Dutch numeric parity validator for localized dates

### What changed
- Updated `tools/validate_index_bilingual_numeric_parity.py` so it strips ISO dates, English long dates, Dutch long dates, section headers and report-token filenames before comparing financial numeric tokens.
- Re-triggered the NL draft workflow request for report token `260518`.

### Why
The first numeric parity validator was too broad. It counted date components as investment numbers, so valid Dutch date localization such as `2026-05-18` to `maandag 18 mei 2026` caused a false parity failure.

### Affected files
- `tools/validate_index_bilingual_numeric_parity.py`
- `changelog.md`

### Validation / evidence
- The original failure was at numeric parity with `first_diff_at=1 en='05' nl='18'`, which is consistent with date-localization noise rather than financial-number drift. The workflow has been re-triggered after the validator fix.

---

## 2026-05-19 — Improve Dutch draft localization quality gates

### What changed
- Reworked the Dutch markdown generator to avoid generic short word replacements that corrupted words such as `Holdings` into `Houdenings`.
- Added more deterministic phrase, sentence and table-header translations for the current English Weekly Index report structure.
- Added targeted fixups for known bad localization artifacts.
- Tightened the Dutch language contract so it fails on obvious English residue and known bad artifacts.

### Why
The first Dutch draft validated structurally and numerically but still contained too much mixed English/Dutch copy. The bilingual path should fail fast on obvious localization artifacts before moving toward render or delivery.

### Affected files
- `tools/generate_index_nl_report.py`
- `tools/validate_index_nl_language_contract.py`
- `changelog.md`

### Validation / evidence
- Next validation step is a fresh NL draft run for report token `260518` under the stricter language contract.

---

## 2026-05-19 — Add regex fallback translations for Dutch Top 3 action lines

### What changed
- Added line-level regex fallback translations for the `Top 3 actions this week` block in the Dutch markdown generator.
- The fallback catches action lines starting with `Keep QQQ`, `Test SPY`, and `Force IWM` even when exact sentence replacement misses due to spacing, punctuation, or workflow-context differences.

### Why
The stricter Dutch language validator correctly blocked remaining English residue in the Top 3 action block. Exact sentence replacement was not robust enough, so those high-visibility lines needed line-level protection.

### Affected files
- `tools/generate_index_nl_report.py`
- `changelog.md`

### Validation / evidence
- Previous workflow failure: Dutch language contract failed on `Keep QQQ` and `Test SPY`. Next validation step is a fresh NL draft run for token `260518`.

---

## 2026-05-20 — Migrate Weekly Index NL draft to native state-driven renderer

### What changed
- Added a native Dutch Weekly Index renderer that builds the NL markdown directly from shared state and ranking artifacts instead of translating the completed English markdown line by line.
- Updated the NL draft workflow to call the native renderer.
- Reworked EN/NL numeric parity to become state-aware: it verifies shared authoritative portfolio numbers, positions, weights, returns, P/L and contribution values instead of requiring every incidental markdown number to appear in the same order.

### Why
The English-to-Dutch post-translation path was becoming residue-driven and fragile. The proven `weekly-etf` approach uses runtime/state-driven native Dutch rendering, which is more deterministic and avoids endless patching of English fragments like `Keep QQQ` and `Test SPY`.

### Affected files
- `tools/render_index_nl_report_from_state.py`
- `.github/workflows/build-weekly-index-nl-draft.yml`
- `tools/validate_index_bilingual_numeric_parity.py`
- `changelog.md`

### Validation / evidence
- Next validation step is a fresh NL draft run for token `260518` using the native renderer path.

---

## 2026-05-20 — Accept equivalent number formats in bilingual parity

### What changed
- Updated the state-aware EN/NL numeric parity validator to accept equivalent numeric display formats.
- The validator now tolerates integer shares such as `44` versus `44.00`, comma-formatted values such as `2,977.78` versus `2977.78`, and signed percentage formats.

### Why
The native Dutch renderer passed language and section validation, but numeric parity failed because the English markdown uses compact or comma-formatted values while the state-driven NL renderer uses normalized decimal values. These are equivalent and should not block validation.

### Affected files
- `tools/validate_index_bilingual_numeric_parity.py`
- `changelog.md`

### Validation / evidence
- Previous native-renderer draft failed only on numeric-format mismatches for shares and P/L values, not on language or section parity. Next validation step is a fresh native NL draft run for token `260518`.

---

## 2026-05-20 — Add Dutch draft HTML/PDF render validation path

### What changed
- Extended the Dutch draft workflow to install the PDF rendering dependencies used by production delivery.
- Added a render-only step for the Dutch markdown draft using the existing premium Weekly Index renderer.
- Added Dutch draft validation for Analyst visual distinction, render polish and ticker links.
- Extended the Dutch draft commit step to include NL clean markdown, delivery HTML, PDF, equity-curve image and delivery manifest.

### Why
The Dutch markdown path now validates language, sections and numbers. The next safety gate is render quality before any bilingual email delivery is added. This keeps NL output draft-only while proving the PDF/HTML artifacts can be generated and inspected.

### Affected files
- `.github/workflows/build-weekly-index-nl-draft.yml`
- `changelog.md`

### Validation / evidence
- Next validation step is a fresh NL draft run for token `260518` that produces `weekly_indices_review_nl_260518_delivery.html` and `weekly_indices_review_nl_260518.pdf` without sending email.

---

## 2026-05-20 — Port ETF-style bilingual render adapter to Weekly Index

### What changed
- Added `send_index_report_bilingual.py`, a bilingual render adapter that follows the proven Weekly ETF pattern: keep native Dutch markdown, adapt Dutch headings and content labels only at render time, and reuse the existing premium Weekly Index rendering stack.
- The adapter validates Dutch companion markdown using Dutch headings and disclaimer language, then converts section headings and key labels into renderer-compatible forms before final HTML/PDF generation.
- Updated the NL draft workflow to call the bilingual renderer instead of the English-only renderer.

### Why
The previous NL draft render failed because the English renderer required English headings such as `Executive Summary`. Weekly ETF solved this class of problem by making the delivery layer bilingual-aware instead of building one-off Dutch wrappers. This ports that pattern into Weekly Index while keeping email delivery disabled for Dutch drafts.

### Affected files
- `send_index_report_bilingual.py`
- `.github/workflows/build-weekly-index-nl-draft.yml`
- `changelog.md`

### Validation / evidence
- Previous render failure was caused by English-only heading validation. Next validation step is a fresh NL rendered draft run for token `260518` using the bilingual adapter.

---

## 2026-05-20 — Allow Dutch Analyst visual labels in validator

### What changed
- Updated the Analyst visual distinction validator so it accepts either English or Dutch labels for the Analyst transition.
- The invariant visual requirements remain unchanged: `analyst-hero`, petrol-teal `#0F5B5C`, and print page-break CSS must still be present.

### Why
The Dutch HTML/PDF render now succeeds, but the validator still required English text labels: `PART II` and `Research depth, scenario framing and implementation detail`. The Dutch render correctly localizes these to `DEEL II` and `Onderzoeksdiepte, scenario’s en implementatiedetail`, so the validator needed bilingual label aliases rather than weakening the visual contract.

### Affected files
- `tools/validate_index_analyst_visual_distinction_for_report.py`
- `changelog.md`

### Validation / evidence
- Previous workflow failure occurred after successful Dutch render and failed only because the visual validator required English labels. Next validation step is a fresh NL rendered draft run for token `260518`.

---

## 2026-05-20 — Linkify native Dutch report tickers before render

### What changed
- Added a deterministic ticker-link normalization script for Weekly Index reports.
- Updated the NL draft workflow so the native Dutch markdown is linkified before HTML/PDF rendering and ticker-link validation.
- The linkifier covers the same visible tradable proxy universe as the ticker-link validator, including candidate proxies such as `EWT`.

### Why
The Dutch rendered draft passed render, visual distinction and polish checks, but ticker-link validation failed because `EWT` was visible in the Dutch report without a TradingView link. This normalizes known proxy tickers at the markdown stage so the existing renderer and validator receive already-linked tickers.

### Affected files
- `tools/linkify_index_report_tickers.py`
- `.github/workflows/build-weekly-index-nl-draft.yml`
- `changelog.md`

### Validation / evidence
- Previous workflow failure occurred only at the ticker-link gate: `visible tickers missing TradingView links ... EWT`. Next validation step is a fresh NL rendered draft run for token `260518`.
