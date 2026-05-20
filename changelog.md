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
- Next validation step is a fresh production run through `control/run_queue/weekly_indices_report_request_*.md`.
