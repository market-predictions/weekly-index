# Weekly Indices Review report request

requested_at_utc: 2026-05-12T23:00:00Z
requested_run_date: 2026-05-12
mode: production
report_type: weekly_indices_review
request_source: ChatGPT

## Request
Generate and publish a fresh Weekly Indices Review Report.

## Required production path
Use the upgraded index-native workflow:

pricing pass
→ benchmark-vs-proxy pricing contract
→ macro regime snapshot
→ relative strength snapshot
→ index macro policy pack
→ candidate evidence packs
→ candidate ranking and discovery coverage
→ runtime index report state
→ alternative duels
→ decision-grade short radar
→ alternative-duel and short-radar validators
→ artifact-driven report section assembly
→ final report composition
→ report-vs-ranking reconciliation
→ compactness validator
→ recommendation scorecard validator
→ HTML/PDF validation
→ email delivery
→ run manifest and artifact commit-back

## Hard requirements
- Use fresh pricing before report generation.
- Keep benchmark-index analysis and tradable-proxy valuation separate.
- Build and persist the macro policy pack under output_indices/macro/.
- Build and persist runtime report state under output_indices/runtime/.
- Keep defensive / inverse candidates separate from long-side opportunities.
- Do not allow raw artifact labels such as board_capacity, near_miss, or ruled_out into client-facing report text.
- Do not claim delivery success without a real manifest or delivery receipt.
