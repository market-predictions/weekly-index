# Weekly Indices Review report request

requested_at_utc: 2026-05-13T00:35:00Z
requested_run_date: 2026-05-13
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
→ client-facing scaffold/process-language scrub
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
- Use the broadened discovery catalog from pricing_indices/catalog.py.
- Include South Korea, Taiwan, Brazil, Mexico, South Africa, Indonesia, Saudi Arabia, Australia, U.S. factor/style alternatives, and other extended regions in the scan universe where pricing/proxy evidence is available.
- Keep the main board compact; do not crowd the client report.
- Show broad coverage through the coverage checkpoint and universe scan checkpoint.
- Use the new Portfolio sleeve / Benchmark index / Tradable proxy terminology.
- Build and persist the macro policy pack under output_indices/macro/.
- Include the new geopolitical_regime field from the macro policy pack in the Executive Summary.
- Do not show Pending classification for Geopolitical regime if the macro pack provides a current geopolitical regime.
- Build and persist runtime report state under output_indices/runtime/.
- Render Executive Summary and Portfolio Action Snapshot from current index_portfolio_state and macro/latest.
- Render Section 11 from the alternative-duel and short-radar artifacts.
- Keep defensive / inverse candidates separate from long-side opportunities.
- Include Alternative Duel Table in Section 11.
- Use dynamic Alternative Duel required triggers based on 20d edge, 60d edge, momentum state and portfolio-fit risk.
- Do not use the old generic trigger text: Needs positive 60d edge plus portfolio-fit improvement before funding.
- Run tools/scrub_index_client_report.py before compactness validation.
- Block stale NAV or stale pricing-date leakage in executive/action sections, while allowing the report date itself.
- Preserve ticker-link spacing in delivery HTML; no SPYagainst, QQQoverlap, IWMand, or EEMthrough artifacts.
- Render Portfolio Action Snapshot from the table-based Section 2, not from legacy subsection parsing.
- Do not allow raw artifact labels such as board_capacity, near_miss, ruled_out, TBD, live repo state, workflow pricing, production workflow should refresh, artifact rebuild, or pricing/ranking rebuild into client-facing report text.
- Do not claim delivery success without a real manifest or delivery receipt.

## Recent fixes under validation
- Broadened scan universe and candidate grouping.
- Proxy eligibility metadata added.
- Geopolitical regime added to macro policy pack and executive summary.
- Section 4 renamed to Portfolio sleeve / Benchmark index / Tradable proxy terminology.
- Section 11 and Section 16 now expose broader scan coverage without crowding the main board.
