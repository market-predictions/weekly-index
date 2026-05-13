# Weekly Indices Review report request

requested_at_utc: 2026-05-13T00:55:00Z
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
- Use layered_close_discovery_v1 for benchmark and tradable-proxy closes.
- Use provider order: Yahoo history → Twelve Data → FMP → Alpha Vantage → carried-forward prior valid close.
- Persist provider/source/status diagnostics in output_indices/pricing/index_price_audit_*.json.
- Keep benchmark-index analysis and tradable-proxy valuation separate.
- Keep the main board compact; do not crowd the client report.
- Show broad coverage through the coverage checkpoint and universe scan checkpoint.
- Use the new Portfolio sleeve / Benchmark index / Tradable proxy terminology.
- Build and persist the macro policy pack under output_indices/macro/.
- Include geopolitical_regime from the macro policy pack in the Executive Summary.
- Do not show Pending classification for Geopolitical regime if the macro pack provides a current geopolitical regime.
- Render Executive Summary and Portfolio Action Snapshot from current index_portfolio_state and macro/latest.
- Render Section 11 from the alternative-duel and short-radar artifacts.
- Keep defensive / inverse candidates separate from long-side opportunities.
- Include Alternative Duel Table in Section 11.
- Use dynamic Alternative Duel required triggers based on 20d edge, 60d edge, momentum state and portfolio-fit risk.
- Do not use the old generic trigger text: Needs positive 60d edge plus portfolio-fit improvement before funding.
- Add the ETF-style Tradable Proxy Performance table in Section 15.
- Performance table must include: Portfolio sleeve, Benchmark index, Tradable proxy, Weight %, 1w return, 1m return, 3m return, Since-entry, P/L EUR, Contribution %.
- Validate the performance table against output_indices/index_portfolio_state.json performance metrics.
- Run tools/scrub_index_client_report.py before compactness validation.
- Block stale NAV or stale pricing-date leakage in executive/action sections, while allowing the report date itself.
- Preserve ticker-link spacing in delivery HTML; no SPYagainst, QQQoverlap, IWMand, or EEMthrough artifacts.
- Do not allow raw artifact labels such as board_capacity, near_miss, ruled_out, TBD, live repo state, workflow pricing, production workflow should refresh, artifact rebuild, or pricing/ranking rebuild into client-facing report text.
- Do not claim delivery success without a real manifest or delivery receipt.

## Recent fixes under validation
- Layered close discovery implemented in pricing_indices/data_sources.py and pricing_indices/run_pricing_pass.py.
- Pricing contract validates layered pricing model, provider order, provider/source diagnostics, and performance metrics.
- Tradable Proxy Performance table added in pricing_indices/compose_final_report.py.
- State consistency validator now requires the Tradable Proxy Performance table and required columns.
