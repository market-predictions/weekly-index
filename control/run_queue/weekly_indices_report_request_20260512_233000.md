# Weekly Indices Review report request

requested_at_utc: 2026-05-12T23:30:00Z
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
→ state-consistency validator
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
- Render Executive Summary and Portfolio Action Snapshot from current index_portfolio_state and macro/latest.
- Render Section 11 from the alternative-duel and short-radar artifacts.
- Keep defensive / inverse candidates separate from long-side opportunities.
- Include Alternative Duel Table in Section 11.
- Block stale NAV or stale pricing-date leakage in executive/action sections, while allowing the report date itself.
- Do not allow raw artifact labels such as board_capacity, near_miss, ruled_out, TBD, live repo state, or pricing/ranking rebuild into client-facing report text.
- Do not claim delivery success without a real manifest or delivery receipt.

## Known follow-up
The full ETF-style robust layered close-price discovery model is tracked in NEXT_ACTIONS and is not yet fully ported to weekly-index. This run validates the current state-driven composition and validation layer first.
