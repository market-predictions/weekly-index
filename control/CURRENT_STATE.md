# Weekly Index OS — Current State

## Snapshot date
2026-05-19

## Current baseline

`market-predictions/weekly-index` is now a production-style Weekly Index Review system with a validated English report baseline.

The active production product is the **Weekly Indices Review**. The AEX options track remains preserved but parked.

## Current production architecture

### Decision framework
The report decides:
- current equity-index regime
- funded exposure actions
- long-side opportunity board
- defensive / inverse opportunity readiness
- capital re-underwriting of funded exposures
- portfolio value, contribution and continuity

### Input / state contract
Authoritative state comes from:
- explicit requested close date
- benchmark-index closes for analysis
- tradable proxy closes for implemented portfolio valuation
- `output_indices/index_portfolio_state.json`
- `output_indices/index_valuation_history.csv`
- `output_indices/index_recommendation_scorecard.csv`
- pricing audits under `output_indices/pricing/`
- candidate ranking and discovery coverage artifacts
- macro, research, alternative-duel and short-radar artifacts

### Output contract
The current English output contract is:
- Investor Report first
- Analyst Report second
- visible Part II / Analyst Report transition
- petrol-teal Analyst identity
- Section 7 owns equity curve plus Tradable Proxy Performance
- Section 15 owns holdings and cash only
- table tickers must be TradingView-linked
- equity curve must be embedded in the PDF
- x-axis labels must be print-safe and non-overlapping
- native list markers must be converted to inline markers to avoid PDF ghost bullets

### Operational runbook
The workflow now resolves the requested close date and explicit report token before generation. A May 18 requested close must produce token `260518` and the canonical report path:

```text
output_indices/weekly_indices_review_260518.md
```

The production workflow passes the explicit report token/path through token-sensitive steps instead of silently selecting an older report.

## Validated fixes now considered baseline

The following items are no longer open issues:

1. **Fresh pricing / report-token discipline**
   - Latest validated report: `output_indices/weekly_indices_review_260518.md`
   - Requested close date: `2026-05-18`
   - Portfolio value: EUR `111,116.08`

2. **Section placement**
   - Section 7 contains the equity curve and Tradable Proxy Performance.
   - Section 15 contains holdings/cash only.

3. **Analyst Report visual distinction**
   - Analyst Report uses the frozen petrol-teal palette.
   - Section 10 cards are white inside the subtle cool-grey Analyst panel.

4. **Clickable tickers**
   - Known table tickers are linked to TradingView.

5. **PDF rendering polish**
   - Native list markers are inlined to prevent ghost bullets.
   - Equity curve chart labels use print-safe spacing.

6. **Recommendation/state continuity**
   - Recommendation scorecard is generated and persisted.
   - Report-tokened artifacts now use the requested close token.

7. **Changelog discipline**
   - Root-level `changelog.md` now records meaningful repo changes.

## Current strengths

- English Weekly Index report is production-validated for May 18 close.
- Pricing-first workflow and explicit token handling are in place.
- Full-universe breadth coverage exists across U.S., Europe, UK, Switzerland, Japan, Canada, Greater China, India, Korea/Taiwan, LatAm, ASEAN, Middle East and EM broad.
- Section 11 separates long opportunities from defensive / inverse tools.
- Recommendation scorecard provides capital re-underwriting memory.
- Visual structure clearly separates Investor Report from Analyst Report.
- Render validations catch key output-contract regressions.

## Current weaknesses / known future improvements

### 1. Recommendation scorecard still needs deeper data backing
The scorecard is useful, but relative-strength duels and factor exposure are still partly heuristic. Future work should add stronger 1-month / 3-month relative-strength history and better factor lookthrough.

### 2. Bilingual output is not yet implemented
The next product upgrade is a Dutch companion report with the same state, numbers, section structure and layout contract as the English report.

### 3. Control layer needs to stay current after meaningful changes
All future meaningful changes must update `changelog.md`, and durable operating decisions should also update control files when they change the baseline.

## Current status label

**English Weekly Index Review baseline is stable and validated. The next major workstream is the bilingual Weekly Index model: Dutch report generation using the same data/state/numbers, with section parity, numeric parity, Dutch terminology discipline, and no English date leakage.**
