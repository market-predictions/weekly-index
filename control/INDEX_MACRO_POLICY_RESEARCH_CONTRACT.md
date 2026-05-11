# Index Macro & Policy Research Contract

## Purpose

This contract ports the ETF macro/policy/regime lesson into an index-native workflow.

The Weekly Indices Review should ingest broad macro, policy, central-bank, breadth, credit, USD and cross-asset information as a machine-readable input layer, but transfer only the most decision-relevant points into the client report.

## Layer distinction

### 1. Decision framework

No Add, Replace, Reduce, Hedge, or Inverse-ready decision should be made unless it is consistent with:

- current market regime
- breadth / relative-strength confirmation
- central-bank and real-rate context
- USD and liquidity pressure
- benchmark-index behavior
- tradable-proxy implementation evidence
- explicit invalidation and trigger rules

### 2. Input / state contract

The workflow should build a macro policy pack before candidate ranking and report composition:

```text
output_indices/macro/index_macro_policy_pack_YYYYMMDD.json
output_indices/macro/latest.json
```

The pack is runtime state. It is not a long prose memo.

Minimum schema:

```json
{
  "report_date": "YYYY-MM-DD",
  "regime": {
    "current": "Risk-on narrow US mega-cap leadership",
    "previous": "Unknown",
    "confidence": 0.70,
    "what_changed": [],
    "portfolio_implication": ""
  },
  "central_banks": {
    "fed": {},
    "ecb": {},
    "boj": {},
    "boe": {},
    "pboc": {}
  },
  "macro_signals": {
    "real_rates": {},
    "usd": {},
    "credit": {},
    "duration": {},
    "equity_breadth": {},
    "volatility": {},
    "commodities": {}
  },
  "region_implications": {},
  "long_lane_adjustments": {},
  "defensive_inverse_adjustments": {},
  "report_digest": {}
}
```

### 3. Output contract

The client report may only transfer compact digest items:

- current regime
- one-line confidence / caveat
- max 3 what-changed bullets
- max 3 portfolio implications
- max 2 central-bank or policy points
- max 1 risk-watch statement

The full macro pack must not be dumped into the report.

### 4. Operational runbook

The production workflow should run:

```text
pricing pass
→ macro regime snapshot
→ relative-strength snapshot
→ macro policy pack
→ candidate evidence and ranking
→ runtime report state
→ compact report composition
→ validators
→ render/send
```

## Index-native authority rules

- Benchmark closes are used for market analysis.
- Tradable proxy closes are used for implemented portfolio valuation.
- Defensive / inverse candidates must remain separate from long-side opportunities.
- Macro regime can support or penalize a candidate, but cannot override missing pricing, missing benchmark/proxy distinction, or missing trigger/invalidation logic.
- Report prose is a summary of artifacts, not the source of truth.

## Non-goals

- Do not create a sprawling macro newsletter.
- Do not mix inverse tools into the long opportunity board.
- Do not let raw artifact labels such as `board_capacity`, `near_miss`, or `ruled_out` appear in client-facing text.
