# Weekly Index Capital Re-underwriting Rules

## Purpose

This file is the index-native decision-framework addendum adapted from the mature Weekly ETF Review discipline layer.

It does not replace `index.txt`. It tightens the decision layer between current-position scoring, long-side candidate ranking, defensive / inverse radar, and the final action table.

## Core principle

Every funded index exposure must earn capital again each run.

The required question is:

> If this exposure did not exist today, would we initiate it now, at this weight, with fresh capital?

## Mandatory capital re-underwriting layer

Run this layer after fresh pricing and candidate ranking, and before the final action table.

For every current funded exposure, assess:

1. Fresh cash test
2. Thesis versus implementation split
3. Relative alternative duel when weak or replaceable
4. Contribution / drag test
5. Factor-overlap test
6. Breadth and concentration test
7. Hedge / inverse validity test where relevant
8. Cash policy test
9. Action-clock / inertia test

## Fresh cash test

For every holding, store and, where decision-relevant, report:

| Test | Allowed values |
|---|---|
| Would initiate today? | Yes / Smaller / No / Unresolved |
| Would initiate at current weight? | Yes / No / Unresolved |
| Fresh-cash implication | Add / Hold / Reduce / Replace / Close / Watch one more week |

Rules:
- If a holding would not be initiated today at any size, it cannot remain an unqualified Hold.
- If a holding would only be initiated smaller, it must be tagged Reduce candidate or Hold under review.
- Any override must name the reason and maximum review window.

## Thesis versus implementation split

Separate every exposure into:

| Score | Meaning |
|---|---|
| Thesis score | Is the index / region / style thesis still valid? |
| Implementation score | Is this proxy, at this price, weight, trend, and liquidity profile still the right implementation? |

A valid macro thesis does not automatically justify keeping the current proxy or current weight.

## Relative alternative duel

A position must be compared with a named alternative when any are true:
- it is Hold but replaceable
- it is a Reduce candidate
- it is down more than 10% from average entry
- it has underperformed the portfolio for two consecutive runs
- a stronger long-side challenger or inverse hedge is surfaced in Section 11

Minimum duel fields:

| Test | Current holding | Alternative | Winner |
|---|---:|---:|---|
| 1-month relative strength | | | |
| 3-month relative strength | | | |
| Liquidity / spread | | | |
| Theme / benchmark purity | | | |
| Drawdown from recent high | | | |
| Portfolio differentiation | | | |
| Final verdict | | | |

If data is incomplete, label the duel unresolved. Do not use missing data as permission for indefinite Hold.

## Breadth and factor-overlap test

Assess effective exposure, not only ticker count.

Required factor map:

| Factor | Exposure level | Main contributors | Concern |
|---|---|---|---|
| U.S. equity beta | Low / Medium / High | | |
| U.S. tech / growth leadership | Low / Medium / High | | |
| Small-cap / financing sensitivity | Low / Medium / High | | |
| Non-U.S. developed markets | Low / Medium / High / Zero | | |
| Emerging markets / dollar sensitivity | Low / Medium / High / Zero | | |
| Defensive / inverse hedge readiness | Low / Medium / High | | |

Rules:
- If a single factor exceeds roughly 40% effective exposure, call it concentration.
- If non-U.S. exposure is low, state whether that is an intentional U.S. exceptionalism bet.
- If SPY and QQQ are both large weights, explicitly test whether SPY still diversifies or mostly duplicates U.S. mega-cap growth beta.
- If IWM remains funded while small-cap breadth weakens, require a direct alternative or inverse-lane comparison.

## Hedge / inverse validity test

For any defensive or inverse lane, assess:

| Hedge / inverse test | Allowed values |
|---|---|
| Does it protect the actual portfolio risk? | Yes / No / Unclear |
| Is the trigger active? | Yes / No / Watch |
| Is the current price verified? | Yes / No |
| Is the holding period tactical? | Yes / No |
| Better hedge candidate? | Ticker / None / Unresolved |

Rules:
- Inverse products are tactical tools, not default strategic holdings.
- A short opportunity must name trigger and invalidation.
- A short opportunity cannot be mixed into the long-side opportunity board.

## Cash policy test

Classify cash each run:

| Cash type | Meaning |
|---|---|
| Tactical reserve | Deliberately held for pullback |
| Whole-share residual | Leftover from implementation |
| Risk reserve | Held because regime uncertainty is elevated |
| Deployment candidate | Should be allocated this run |

Rules:
- If cash is above 3% and at least one long lane is Actionable now, explain why cash is not deployed.
- If cash is above 5%, call it a meaningful portfolio position.

## Action-clock / inertia test

A weak or replaceable index exposure cannot remain indefinitely in ambiguous Hold.

Rules:
- `Hold but replaceable` may not persist for more than two consecutive runs without direct decision: upgrade, reduce, replace, or close.
- A position down more than 10% and below a 4.00 score must be re-underwritten.
- A funded exposure underperforming the portfolio by more than 7 percentage points for two consecutive runs must be re-underwritten.
- Any override must include a next-review trigger and maximum review window.

## Required report integration

### Section 6 — Bottom Line
Mention the single most important discipline issue if one exists:
- concentration
- cash deployment
- weak breadth
- short-radar activation
- replaceable holding
- stale pricing

### Section 10 — Current Position Review
Where practical include:
- Would initiate today?
- Would initiate at current weight?
- Thesis score
- Implementation score
- Best alternative
- Required next action

### Section 11 — Best New Index Opportunities
Keep long-side opportunities separate from defensive / inverse opportunities.

### Section 13 — Final Action Table
If the fixed table cannot be extended, encode discipline in `Short Reason` and preserve the full fields in the machine-readable scorecard.

### Section 16 — Continuity Input
Carry forward:
- positions under review
- replaceable timer
- best alternative
- factor concentration note
- cash policy note
- short-radar activation candidate

## Machine-readable state requirement

Every canonical Weekly Indices Review should be derivable into:

`output_indices/index_recommendation_scorecard.csv`

This scorecard is the explicit memory layer for:
- fresh cash test
- thesis score
- implementation score
- replaceable status
- action-clock timer
- best alternative
- contribution drag
- factor overlap
- hedge / inverse validity
- cash policy
- required next action
- override reason
