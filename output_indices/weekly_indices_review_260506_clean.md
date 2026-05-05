# Weekly Indices Review 2026-05-06

> *This report is for informational and educational purposes only; please see the disclaimer at the end.*

## 1. Executive Summary
- Primary regime: Policy Transition / Mixed Regime
- Geopolitical regime: Elevated but localized
- Main takeaway: Run the full upgraded Weekly Index workflow end to end: fresh closing prices first, full-universe breadth, long opportunities, short opportunities radar, capital re-underwriting scorecard, render validation, and email delivery.
- This run validates the ETF-derived capital re-underwriting layer inside `weekly-index`.
- The production workflow must refresh pricing first, rebuild research and ranking artifacts, compose live artifact-driven sections, derive the recommendation scorecard, validate render/PDF, then send.
- Do not treat this scaffold as the final analysis if the workflow replaces artifact-driven sections successfully.

## 2. Portfolio Action Snapshot
### Add
- None before the live pricing/ranking rebuild.
### Hold
- S&P 500 (**SPY**)
- Nasdaq 100 (**QQQ**)
- Russell 2000 (**IWM**)
- Emerging Markets (**EEM**)
### Hold but replaceable
- Russell 2000 (**IWM**)
- Emerging Markets (**EEM**)
### Reduce
- None before the live pricing/ranking rebuild.
### Close
- None before the live pricing/ranking rebuild.
### Best replacements to fund
- China large cap (FXI), S&P/TSX 60 (EWC), and FTSE MIB (EWI) remain the closest replacement candidates, subject to confirmation and portfolio-fit discipline.
### Top 3 actions this week
1. Fetch and persist fresh closing prices first.
2. Rebuild the long-side opportunity board and full-universe breadth checkpoint.
3. Validate the index recommendation scorecard before render/email.
### Top 3 risks this week
1. Fresh closing-price coverage is insufficient for a genuinely fresh report.
2. The long board remains too narrow despite the broader scan universe.
3. Weak or replaceable holdings remain vague instead of producing alternatives, triggers, or override reasons.

## 3. Global Regime Dashboard
- Primary regime remains mixed / transitionary until the live macro snapshot confirms otherwise.
- Geopolitical regime remains elevated but localized until the current run’s research layer confirms otherwise.
- Risk appetite, breadth, rates, credit, dollar pressure, oil pressure, and regional dispersion should be rebuilt from current production artifacts.
- Portfolio implication: stay invested, but keep a clean defensive / inverse radar if breadth, liquidity, or leadership deteriorates.

## 4. Index Opportunity Board

| Exposure | Benchmark / public index | Implementation proxy | Regional group | Score | Status | Why it is on the board |
|---|---|---|---|---:|---|---|
| Nasdaq 100 | Nasdaq 100 | QQQ | U.S. core leadership | 3.00 | Funded | Growth leadership remains a core engine in the current opportunity set. |
| Emerging Markets | Emerging Markets | EEM | EM broad | 2.99 | Funded | Emerging markets add a measured non-U.S. risk sleeve while the dollar backdrop is less hostile. |
| Russell 2000 | Russell 2000 | IWM | U.S. core leadership | 2.72 | Funded | Domestic breadth improves diversification without dominating the book. |
| S&P 500 | S&P 500 | SPY | U.S. core leadership | 2.61 | Funded | Core U.S. large-cap exposure remains the cleanest starting anchor. |
| Nikkei 225 | Nikkei 225 | EWJ | developed Asia-Pacific | 2.35 | Surfaced | Improves breadth or fills an important portfolio gap without forcing a low-conviction rotation. |

The board remains intentionally compact. The strongest omitted regional challenger this run is **FTSE MIB (EWI)**, which remains close enough to matter without displacing a higher-ranked funded exposure.

## 5. Key Risks / Invalidators
- Growth slows more sharply than the current market-implied regime suggests.
- Inflation, oil, or policy pressure reaccelerates.
- U.S. breadth weakens and small caps lose relative support.
- Dollar strength pressures EM and international allocations.
- A pricing, research, ranking, scorecard, render, PDF, or email-send validation step fails.

## 6. Bottom Line
- The portfolio remains constructive but selective.
- U.S. leadership remains the core engine, but concentration must be watched.
- IWM and EEM remain funded but under review versus clearer challengers.
- Inverse instruments are not base-case positions, but the hedge map is ready if breadth breaks.

## 7. Equity Curve and Portfolio Development

- Starting capital (EUR): 100000.00
- Current portfolio value (EUR): 109869.46
- Since inception return (%): 9.87
- Equity-curve state: Live tracked
- Pricing basis requested close date: 2026-05-05
- FX reference date: 2026-05-05
- Notes: Holdings and NAV are rebuilt from the pricing/state layer for the requested close date 2026-05-05.

| Date | Portfolio value (EUR) | Comment |
|---|---:|---|
| 2026-04-20 | 106472.03 | Pricing basis close 2026-04-20 |
| 2026-04-21 | 105989.18 | Pricing basis close 2026-04-21 |
| 2026-04-22 | 106143.07 | Pricing basis close 2026-04-22 |
| 2026-04-24 | 106707.13 | Pricing basis close 2026-04-24 |
| 2026-04-27 | 105772.19 | Pricing basis close 2026-04-27 |
| 2026-04-30 | 107173.81 | Pricing basis close 2026-04-30 |
| 2026-05-01 | 107643.74 | Pricing basis close 2026-05-01 |
| 2026-05-04 | 108478.51 | Pricing basis close 2026-05-04 |
| 2026-05-05 | 109869.46 | Pricing basis close 2026-05-05 |

`EQUITY_CURVE_CHART_PLACEHOLDER`

## 8. Regional / Style Allocation Map
- U.S. remains the funded core before the live artifact rebuild.
- Europe, UK, Switzerland, Japan, Canada, Australia, Greater China, India, and EM broad must remain visible in the breadth checkpoint.
- Cash preserves optionality.
- Defensive / inverse opportunities should be visible but clearly labelled as tactical hedges.

## 9. Second-Order Effects Map
- Relief tone supports the current funded book if breadth remains intact.
- Rates and credit conditions determine whether higher-beta exposures can displace funded positions.
- Dollar pressure determines whether EM and international challengers deserve more capital.
- Oil and commodity pressure affect Europe, Australia, Canada, and inflation-sensitive sleeves differently.
- If breadth breaks, the best short opportunities are likely small caps first, then tech or broad U.S. market hedges depending on leadership failure.

## 10. Current Position Review
### S&P 500 / SPY
- Would initiate today: likely yes, pending live ranking rebuild.
- Would initiate at current weight: pending concentration review versus QQQ.
- Best alternative: VOO / quality exposure / broader non-U.S. challenger.
- Required next action: test SPY / QQQ overlap and U.S. concentration.

### Nasdaq 100 / QQQ
- Would initiate today: likely yes, pending live ranking rebuild.
- Would initiate at current weight: pending duration and mega-cap concentration review.
- Best alternative: QQQM / quality exposure / lower-beta core.
- Required next action: test whether growth leadership still deserves top weight.

### Russell 2000 / IWM
- Would initiate today: unresolved pending breadth confirmation.
- Would initiate at current weight: no if breadth deteriorates.
- Best alternative: VTWO or RWM as inverse tactical hedge.
- Required next action: direct breadth validity and RWM defensive comparison.

### Emerging Markets / EEM
- Would initiate today: unresolved pending dollar and EM confirmation.
- Would initiate at current weight: no if dollar pressure reaccelerates.
- Best alternative: VWO / INDA / EUM as inverse tactical hedge.
- Required next action: direct EM validity and EUM defensive comparison.

## 11. Best New Index Opportunities

### Long-side Opportunities

The strongest omitted regional challenger this run is **China large cap (FXI)**. It improves breadth and remains close enough to the live board to stay visible in the report.

#### 1. China large cap (FXI)

- Regional group: Greater China
- Challenger score: 1.97
- Why it matters: Ranks well internally but remains just below the current publication cutoff.
- Why not on the board yet: Strong challenger, not yet funded

#### 2. S&P/TSX 60 (EWC)

- Regional group: North America ex-U.S.
- Challenger score: 1.74
- Why it matters: Ranks well internally but remains just below the current publication cutoff.
- Why not on the board yet: Strong challenger, not yet funded

#### 3. FTSE MIB (EWI)

- Regional group: continental Europe
- Challenger score: 1.63
- Why it matters: Ranks well internally but remains just below the current publication cutoff.
- Why not on the board yet: Strong challenger, not yet funded

### Best Defensive / Inverse Opportunities

#### 1. Short Russell 2000 via RWM

- Why it matters: the Russell 2000 remains the weakest current held sleeve and is the cleanest bearish expression if tighter conditions and funding stress keep hurting small caps.
- Trigger: further relative breakdown in small-cap breadth.
- Invalidation: clear improvement in small-cap relative strength and easing inflation pressure.

#### 2. Short Nasdaq 100 via PSQ

- Why it matters: this is the cleanest hedge if U.S. growth leadership breaks under higher yields or earnings disappointment.
- Trigger: clear loss of Nasdaq 100 relative leadership or broad de-risking led by large-cap tech.
- Invalidation: renewed earnings-led strength in mega-cap growth and a calmer policy backdrop.

#### 3. Short S&P 500 via SH

- Why it matters: this is the broad-market hedge if selective resilience turns into a wider U.S. risk-off move.
- Trigger: policy or liquidity stress begins to hit the broader index rather than only the weakest sleeves.
- Invalidation: continued S&P 500 earnings resilience and broad participation in upside.

#### 4. Short developed ex-U.S. via EFZ or short Emerging Markets via EUM

- Why it matters: these are the cleaner non-U.S. hedge lanes if Europe or broader emerging markets deteriorate faster than expected.
- Trigger: renewed energy stress, worsening Europe data, or broad EM weakness.
- Invalidation: oil stabilizes, Europe sentiment improves, and EM breadth strengthens.

**Important note:** these inverse instruments are defensive tools, not the base-case allocation. They are most appropriate as tactical hedges or bearish expressions under deterioration, not as default long-term holdings.

### Breadth checkpoint by regional bucket
| Regional bucket | Strongest candidate | Proxy | Challenger score | Current status |
|---|---|---|---:|---|
| U.S. core leadership | Nasdaq 100 | QQQ | 2.20 | Published |
| continental Europe | FTSE MIB | EWI | 1.63 | Near miss |
| UK | FTSE 100 | EWU | 0.84 | Lower priority this run |
| Switzerland | SMI | EWL | 1.06 | Lower priority this run |
| North America ex-U.S. | S&P/TSX 60 | EWC | 1.74 | Near miss |
| developed Asia-Pacific | Nikkei 225 | EWJ | 2.48 | Published |
| Greater China | China large cap | FXI | 1.97 | Near miss |
| India | Nifty 50 | INDA | 0.86 | Lower priority this run |
| EM broad | Emerging Markets | EEM | 2.34 | Published |

### Universe scan checkpoint
| Exposure | Regional group | Proxy | Published? | Challenger score | Why not on the board yet |
|---|---|---|---|---:|---|
| Nikkei 225 | developed Asia-Pacific | EWJ | Yes | 2.48 | Included on the board |
| Emerging Markets | EM broad | EEM | Yes | 2.34 | Included on the board |
| Nasdaq 100 | U.S. core leadership | QQQ | Yes | 2.20 | Included on the board |
| Russell 2000 | U.S. core leadership | IWM | Yes | 2.02 | Included on the board |
| China large cap | Greater China | FXI | No | 1.97 | Strong challenger, not yet funded |
| S&P 500 | U.S. core leadership | SPY | Yes | 1.81 | Included on the board |
| S&P/TSX 60 | North America ex-U.S. | EWC | No | 1.74 | Strong challenger, not yet funded |
| FTSE MIB | continental Europe | EWI | No | 1.63 | Strong challenger, not yet funded |
| DAX | continental Europe | EWG | No | 1.43 | Kept off the compact board by stronger candidates |
| Hang Seng | Greater China | EWH | No | 1.42 | Kept off the compact board by stronger candidates |
| AEX | continental Europe | EWN | No | 1.41 | Kept off the compact board by stronger candidates |
| ASX 200 | developed Asia-Pacific | EWA | No | 1.30 | Relative strength not strong enough yet |
| SMI | Switzerland | EWL | No | 1.06 | Relative strength not strong enough yet |
| IBEX 35 | continental Europe | EWP | No | 0.97 | Relative strength not strong enough yet |
| Nifty 50 | India | INDA | No | 0.86 | Relative strength not strong enough yet |
| FTSE 100 | UK | EWU | No | 0.84 | Relative strength not strong enough yet |
| Euro Stoxx 50 | continental Europe | FEZ | No | 0.52 | Relative strength not strong enough yet |
| CAC 40 | continental Europe | EWQ | No | 0.41 | Relative strength not strong enough yet |

## 12. Portfolio Rotation Plan
- Maintain current holdings unless the rebuilt ranking artifacts indicate a better funded board.
- Use whole shares only.
- Keep residual as cash.
- Do not rotate into a broader region unless the evidence layer and pricing layer reconcile.
- Do not deploy inverse/short instruments unless the tactical deterioration triggers are met.

## 13. Final Action Table
| Ticker | Public index / exposure | Existing/New | Target Weight | Suggested Action | Conviction Tier | Total Score | Portfolio Role | Better Alternative Exists? | Short Reason |
|---|---|---|---:|---|---|---:|---|---|---|
| SPY | S&P 500 | Existing | TBD | Hold | Tier 1 | TBD | Core beta | TBD | Core anchor; test overlap with QQQ |
| QQQ | Nasdaq 100 | Existing | TBD | Hold | Tier 1 | TBD | Growth engine | TBD | Growth leadership; test concentration |
| IWM | Russell 2000 | Existing | TBD | Hold under review | Tier 2 | TBD | Breadth diversifier | RWM if deterioration triggers | Breadth sleeve under review |
| EEM | Emerging Markets | Existing | TBD | Hold under review | Tier 2 | TBD | Non-U.S. risk sleeve | EUM if deterioration triggers | EM sleeve under dollar-pressure review |
| CASH | Residual cash | Existing | TBD | Hold | Tier 1 | — | Optionality | — | Dry powder; classify cash policy |

## 14. Position Changes Executed This Run
- None.
- Any actual position changes must come from the production ranking/state layer, not from this trigger scaffold.

## 15. Current Portfolio Holdings and Cash

- Starting capital (EUR): 100000.00
- Invested market value (EUR): 94302.72
- Cash (EUR): 15566.74
- Total portfolio value (EUR): 109869.46
- Since inception return (%): 9.87
- Pricing basis requested close date: 2026-05-05
- FX reference date: 2026-05-05

| Ticker | Public index / exposure | Shares | Price (local) | Currency | Market value (local) | Market value (EUR) | Weight % |
|---|---|---:|---:|---|---:|---:|---:|
| SPY | S&P 500 | 44 | 723.77 | USD | 31845.88 | 27251.31 | 24.80 |
| QQQ | Nasdaq 100 | 48 | 681.61 | USD | 32717.28 | 27996.99 | 25.48 |
| IWM | Russell 2000 | 90 | 282.56 | USD | 25430.40 | 21761.42 | 19.81 |
| EEM | Emerging Markets | 309 | 65.40 | USD | 20208.60 | 17293.00 | 15.74 |
| CASH | Residual cash | - | 1.00 | EUR | 15566.74 | 15566.74 | 14.17 |

## 16. Continuity Input for Next Run

### Watchlist / dynamic radar memory
| Theme | Regional group | Primary Proxy | Status | Why it stays visible |
|---|---|---|---|---|
| China large cap | Greater China | FXI | Strong challenger | Broad discovery keeps it visible even though it did not make the compact board. |
| S&P/TSX 60 | North America ex-U.S. | EWC | Strong challenger | Broad discovery keeps it visible even though it did not make the compact board. |
| FTSE MIB | continental Europe | EWI | Strong challenger | Broad discovery keeps it visible even though it did not make the compact board. |
| DAX | continental Europe | EWG | Watchlist | Improves breadth or fills an important portfolio gap without forcing a low-conviction rotation. |
| Hang Seng | Greater China | EWH | Watchlist | Broad discovery keeps it visible even though it did not make the compact board. |
| AEX | continental Europe | EWN | Watchlist | Broad discovery keeps it visible even though it did not make the compact board. |
| ASX 200 | developed Asia-Pacific | EWA | Watchlist | Broad discovery keeps it visible even though it did not make the compact board. |
| SMI | Switzerland | EWL | Watchlist | Broad discovery keeps it visible even though it did not make the compact board. |

### Discovery coverage checkpoint
| Regional group | Status | Strongest candidate | Proxy | Score |
|---|---|---|---|---:|
| U.S. core leadership | Surfaced | Nasdaq 100 | QQQ | 2.20 |
| continental Europe | Near miss | FTSE MIB | EWI | 1.63 |
| UK | Lower priority this run | FTSE 100 | EWU | 0.84 |
| Switzerland | Lower priority this run | SMI | EWL | 1.06 |
| North America ex-U.S. | Near miss | S&P/TSX 60 | EWC | 1.74 |
| developed Asia-Pacific | Surfaced | Nikkei 225 | EWJ | 2.48 |
| Greater China | Near miss | China large cap | FXI | 1.97 |
| India | Lower priority this run | Nifty 50 | INDA | 0.86 |
| EM broad | Surfaced | Emerging Markets | EEM | 2.34 |

### Lane continuity notes
- Retained entries: none
- New entries: S&P 500, Nasdaq 100, Russell 2000, Emerging Markets broad
- Dropped entries: none
- Strong challengers not published: Japan large-cap equities, Germany cyclical equities, Europe broad large-cap equities
- What would most likely change the board next run: Cleaner confirmation in Japan or Europe broadens the funded opportunity set next run.

## 17. Disclaimer
This report is provided for informational and educational purposes only. It is not investment, legal, tax, or financial advice, and it is not a recommendation to buy, sell, short, hedge, or hold any security, fund, derivative, or index exposure. It does not take into account the specific investment objectives, financial situation, or particular needs of any recipient. Views are general in nature, may change without notice, and may not be suitable for every investor. Investing and shorting involve risk, including possible loss of principal.