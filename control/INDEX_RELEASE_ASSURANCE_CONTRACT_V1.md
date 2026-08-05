# Weekly Index Release Assurance Contract V1

## Status

```text
contract_id=INDEX_RELEASE_ASSURANCE_CONTRACT_V1
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
project=market-predictions/weekly-index
current_maturity=LEVEL_3_HARD_CI_GATE
target_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
```

## Purpose

Prevent English transport from occurring before the Dutch companion, bilingual parity evidence, benchmark/proxy state and rendered assets are complete.

## Transport model

The existing production workflow is preserved. Its early English send entrypoint becomes a render-and-defer step. The later Dutch entrypoint becomes the only transport release point and sends both languages after one assurance record passes.

## Required evidence

A pre-send `PASS` binds:

- source commit SHA and workflow run ID;
- requested close date and report token;
- benchmark/proxy pricing audit;
- runtime state;
- official portfolio state;
- valuation history and recommendation scorecard;
- candidate ranking and discovery coverage;
- English and Dutch Markdown, delivery HTML, PDF and equity-curve PNG;
- English-send deferral marker;
- exact SHA-256 identities for all evidence and client artifacts.

## Mandatory checks

1. source/date/token identity is valid;
2. all required files exist and have expected formats;
3. control JSON is parseable and bound to the requested close/token;
4. every funded pricing row exposes benchmark symbol, tradable proxy, benchmark close, proxy close and distinct source fields;
5. runtime state references the exact pricing, ranking and coverage artifacts;
6. English and Dutch section-number sets are identical;
7. English and Dutch table financial-number multisets are identical after locale normalization;
8. the early English transport step was deferred rather than sent;
9. all evidence and client artifacts are hashed;
10. implementation and assurance roles are separate;
11. the assurance record validates against the expected release identity.

## Hard gate

- `send_index_report_tv_analyst_distinct.py` preserves validation behavior but defers direct English transport.
- `send_index_report_bilingual.py` builds and validates assurance, then invokes the preserved English and Dutch transport implementations.
- Any assurance failure prevents both transport calls.

## Status semantics

```text
RELEASE_CANDIDATE_READY
ENGLISH_TRANSPORT_DEFERRED
GOVERNANCE_FAIL
GOVERNANCE_PASS_PRE_SEND
TRANSPORT_SENT_UNVERIFIED
DELIVERY_CONFIRMED
```

## LEVEL 4 boundary

Final completion still requires a manifest and independent receiving-system confirmation for both languages bound to the same hashes. Sequential mail transport cannot be treated as atomic delivery.

## Product boundary

This contract applies to the active Weekly Indices Review only. It does not grant authority over the parked AEX Weekly Options track.
