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

## 2026-05-21 — Add Dutch markdown-link residue gate

### What changed
- Added `tools/validate_index_no_markdown_link_residue.py` to fail if Dutch markdown or final delivery HTML contains TradingView markdown-link residue such as `[QQQ](...)`.
- Wired the validator into the Dutch render-validation step before visual/ticker checks and before Dutch send.

### Why
The latest successful run showed the intended delivery-layer linkification working, but ticker-link validation alone can pass while visible markdown syntax remains. This gate preserves the clean-markdown / HTML-linkification architecture and catches regressions before email delivery.

### Affected files
- `tools/validate_index_no_markdown_link_residue.py`
- `.github/workflows/send-weekly-indices-report.yml`
- `changelog.md`

### Validation / evidence
- Latest run from `control/run_queue/weekly_indices_report_request_20260521_112500.md` completed successfully and both EN/NL delivery manifests show `delivery_ok` with PDFs attached.
- The committed Dutch delivery HTML for token `260520` shows TradingView ticker anchors in the hero and Section 2, not visible markdown links.
- This follow-up change adds the explicit guard for future runs; it does not trigger a duplicate report send.

---

## 2026-05-21 — Move Dutch ticker links to HTML delivery layer

### What changed
- Updated `send_index_report_bilingual.py` so Dutch ticker linking is applied to rendered HTML, not pre-written into the Dutch markdown source.
- Added a final HTML ticker-link pass that converts visible ticker tokens and any literal markdown-style TradingView link text into proper HTML anchors.
- Updated `.github/workflows/send-weekly-indices-report.yml` to stop running `tools/linkify_index_report_tickers.py` on the Dutch markdown before render.

### Why
The uploaded Dutch PDF showed raw markdown link syntax such as `[QQQ](https://...)` in custom HTML blocks. Weekly ETF avoids this class of bug by keeping markdown clean and handling rendering/linking in the delivery layer. The Weekly Index Dutch flow had drifted into pre-linkifying markdown before render, which broke custom renderer sections.

### Affected files
- `send_index_report_bilingual.py`
- `.github/workflows/send-weekly-indices-report.yml`
- `changelog.md`

### Validation / evidence
- Uploaded PDF `weekly_indices_review_nl_260520 (1).pdf` showed raw markdown links in the executive hero and body text. Next validation step is a fresh bilingual run and visual inspection that ticker text is clickable without exposing markdown syntax.

---

## 2026-05-21 — Preserve required Dutch terminology after client polish

### What changed
- Updated `tools/render_index_nl_report_from_state_v2.py` so client-facing replacements do not remove terminology that the Dutch language contract requires.
- Restored `Portefeuillesleeve` after the client polish layer accidentally converted it to `Portefeuillepositie`.
- Triggered a fresh bilingual production rerun after the terminology fix.

### Why
The production run sent the English report but blocked the Dutch companion at the language-contract gate because the required Dutch term `Portefeuillesleeve` was missing. The missing term was caused by an over-broad replacement of `sleeve` with `positie`.

### Affected files
- `tools/render_index_nl_report_from_state_v2.py`
- `control/run_queue/weekly_indices_report_request_20260521_011000.md`
- `changelog.md`

### Validation / evidence
- Previous failure: `Dutch language contract failed ... missing required Dutch term: Portefeuillesleeve`.
- Next validation step is the fresh bilingual run triggered by `weekly_indices_report_request_20260521_011000.md`.

---

## 2026-05-21 — Add Dutch executive translation and decision-support layer

### What changed
- Strengthened `tools/render_index_nl_report_from_state_v2.py` with a client-facing Dutch translation layer for internal labels, bucket names, status text and model jargon.
- Added score interpretation in Dutch output so raw candidate scores are displayed with `/5` context and conviction labels.
- Replaced the descriptive Dutch Top 3 Actions block with more concrete week actions focused on no-new-capital discipline, IWM/EWJ/RWM and EEM/FXI/INDA/EUM duels, and hedge readiness.
- Added a visible scan coverage checkpoint for major regions including U.S., Europe, Japan, China/Hong Kong, India, Korea/Taiwan, Latin America, Middle East, ASEAN and Africa.
- Added explicit capital re-underwriting context in the Dutch current-position review.

### Why
The Dutch report had reached functional parity but still exposed too much internal ranking/system language, English bucket labels and passive recommendation language. The goal is to move the Dutch companion closer to ETF-level executive quality: boardroom-ready, decision-useful and less machine-like.

### Affected files
- `tools/render_index_nl_report_from_state_v2.py`
- `changelog.md`

### Validation / evidence
- Code committed to main. Next validation step is a fresh bilingual Weekly Index production run through the existing run-queue trigger.

---

## 2026-05-20 — Make production Weekly Index run bilingual by default

### What changed
- Updated the main production workflow so a fresh Weekly Index run now generates and sends the English report first, then generates the native Dutch companion from the same state, validates EN/NL parity, renders the Dutch HTML/PDF, validates render/ticker contracts, and sends the Dutch email.
- The production commit-back step now also includes Dutch delivery manifests.

### Why
The user expects a fresh production run to produce the canonical English report and Dutch companion by default. The previous production workflow delivered only English, while Dutch had to be triggered through a separate companion workflow.

### Affected files
- `.github/workflows/send-weekly-indices-report.yml`
- `changelog.md`

### Validation / evidence
- Fresh production run delivered both versions, but user review found Dutch/English disparities that required a follow-up fix.

---

## 2026-05-20 — Fix Dutch companion disparities versus English report

### What changed
- Added `tools/render_index_nl_report_from_state_v2.py` as a parity-focused Dutch renderer wrapper over the native state-driven Dutch renderer.
- The v2 renderer fixes the most visible disparities found in the delivered Dutch 260520 PDF:
  - Section 1 now includes the same executive fields as English: primary regime confidence, geopolitical regime, geopolitical implication, what changed, portfolio implication and takeaway.
  - Section 7 valuation history now reads the actual `index_valuation_history.csv` schema (`requested_close_date`, `total_portfolio_value_eur`) instead of falling back to only the latest close.
  - Section 4 now restores the compact-board note about the strongest omitted regional challenger.
  - TradingView markdown links are stripped from the Dutch markdown source so the PDF renderer owns linkification and does not expose raw markdown syntax in executive text.
- Updated `send_index_report_bilingual.py` so Dutch HTML localizes action-snapshot row labels such as Add/Hold/Reduce/Close into Dutch.
- Updated the production workflow to call the v2 Dutch renderer.

### Why
The Dutch PDF was received but did not match the English report closely enough. The most severe user-visible issue was raw markdown links such as `[QQQ](...)` appearing in the Dutch PDF. Other disparities included missing executive-summary fields, only one equity-history row in Dutch, English row labels in Section 2, and missing compact-board context.

### Affected files
- `tools/render_index_nl_report_from_state_v2.py`
- `send_index_report_bilingual.py`
- `.github/workflows/send-weekly-indices-report.yml`
- `changelog.md`

### Validation / evidence
- Previous delivered PDFs compared: English `weekly_indices_review_260520.pdf` had 24 pages while Dutch `weekly_indices_review_nl_260520.pdf` had 20 pages, with raw markdown ticker links visible in Dutch and missing/more compact Dutch content in multiple sections.
- Next validation step is a fresh bilingual production or NL companion rerun after these parity fixes.

---

## 2026-05-21 — Restore Dutch ticker linkification after v2 renderer

### What changed
- Updated the main production workflow so the Dutch companion is linkified immediately after the v2 Dutch renderer writes the markdown.

### Why
The v2 renderer correctly strips raw markdown links to avoid visible `[QQQ](...)` syntax in the Dutch PDF, but the production workflow had not re-applied deterministic ticker linkification before rendering. The fresh run failed only at the Dutch ticker-link gate for `EWT` and `QUAL`.

### Affected files
- `.github/workflows/send-weekly-indices-report.yml`
- `changelog.md`

### Validation / evidence
- Previous fresh bilingual run failed after successful Dutch language, section, numeric, render, visual and polish checks with: `visible tickers missing TradingView links ... EWT, QUAL`.
- Next validation step is another fresh bilingual production run.