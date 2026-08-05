# Weekly Index — Project Governance Bootstrap

```text
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
canonical_standard_location=https://github.com/market-predictions/weekly-etf-eu/blob/main/control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
canonical_location_status=INTERIM_PENDING_CONTROL_PLANE_REPOSITORY
project_repository=market-predictions/weekly-index
project_risk_class=financial_report_delivery_and_model_portfolio_state
adoption_status=documented
enforcement_maturity=LEVEL_1_CHECKLIST
target_enforcement_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
project_specific_assurance_contract=control/INDEX_RELEASE_ASSURANCE_CONTRACT_V1.md
project_specific_assurance_contract_status=PLANNED
production_action=weekly_index_report_generation_and_bilingual_delivery
post_action_confirmation=delivery_manifest_and_independent_receipt
```

## User interface

The user gives one Weekly Index instruction and receives one consolidated project status. The user does not separately coordinate implementation and assurance roles.

## Product boundary

The governance standard applies to both repository tracks when work is consequential:

- Weekly Indices Review — active production product;
- AEX Weekly Options — parked but preserved track.

Governance adoption does not merge their decision frameworks, state contracts, output contracts, or runbooks.

## Current adoption boundary

This file documents the role split and required status semantics. It does not yet claim an independent machine assurance record or hard pre-send gate.

The planned `control/INDEX_RELEASE_ASSURANCE_CONTRACT_V1.md` should verify at least:

- source SHA, requested close, report token, and run identity;
- benchmark-index versus tradable-proxy data separation;
- portfolio-state, valuation-history, scorecard, and report reconciliation;
- Section 7 and Section 15 output-contract placement;
- English and Dutch numeric, structural, and date-localization parity;
- rendered HTML/PDF identities and artifact hashes;
- delivery authorization and manifest;
- independent receiving-system confirmation before final completion.

## Session read rule

For production, release, delivery, model-portfolio mutation, or completion claims, read this file after:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`

Then read the minimum relevant execution and assurance files.

## Prompt invocation

```text
Apply the project's implementation-versus-release-assurance separation. Treat all generated output as a release candidate until independent assurance passes. Do not let implementation certify its own completion. Report action execution separately from independently confirmed outcome.
```
