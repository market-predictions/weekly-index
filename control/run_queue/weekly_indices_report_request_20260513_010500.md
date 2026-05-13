# Weekly Indices Review report request

requested_at_utc: 2026-05-13T01:05:00Z
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
- Keep the main board compact; do not crowd the client report.
- Show broad coverage through the coverage checkpoint and universe scan checkpoint.
- Use Portfolio sleeve / Benchmark index / Tradable proxy terminology.
- Build and persist the macro policy pack under output_indices/macro/.
- Include geopolitical_regime from the macro policy pack in the Executive Summary.
- Render Executive Summary and Portfolio Action Snapshot from current index_portfolio_state and macro/latest.
- Render Section 11 from the alternative-duel and short-radar artifacts.
- Keep defensive / inverse candidates separate from long-side opportunities.
- Include Alternative Duel Table in Section 11.
- Use dynamic Alternative Duel required triggers based on 20d edge, 60d edge, momentum state and portfolio-fit risk.
- Add the ETF-style Tradable Proxy Performance table in Section 15.
- Do not expose internal implementation labels such as layered_close_discovery_v1 in the client-facing report.
- The performance table intro should say that tradable proxy closes drive market value, P/L and contribution, while benchmark index prices remain the analysis reference.
- Run tools/scrub_index_client_report.py before compactness validation.
- Block stale NAV or stale pricing-date leakage in executive/action sections, while allowing the report date itself.
- Preserve ticker-link spacing in delivery HTML.
- Do not allow raw artifact labels such as board_capacity, near_miss, ruled_out, TBD, live repo state, workflow pricing, production workflow should refresh, artifact rebuild, or pricing/ranking rebuild into client-facing report text.
- Do not claim delivery success without a real manifest or delivery receipt.

## Recent fix under validation
pricing_indices/compose_final_report.py now removes the internal pricing model name from the Tradable Proxy Performance intro and replaces it with client-facing wording.
