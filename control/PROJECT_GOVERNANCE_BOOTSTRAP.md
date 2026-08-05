# Weekly Index — Project Governance Bootstrap

```text
standard_id=CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1
canonical_standard_location=https://github.com/market-predictions/control-plane/blob/main/control/CROSS_PROJECT_TWO_ROLE_GOVERNANCE_STANDARD_V1.md
canonical_location_status=CANONICAL_ACTIVE
project_repository=market-predictions/weekly-index
project_risk_class=financial_report_delivery_and_model_portfolio_state
adoption_status=enforced
enforcement_maturity=LEVEL_3_HARD_CI_GATE
target_enforcement_maturity=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
implementation_role=implementation_operations
assurance_role=governance_release_assurance
project_specific_assurance_contract=control/INDEX_RELEASE_ASSURANCE_CONTRACT_V1.md
project_specific_assurance_contract_status=ENFORCED
production_action=weekly_index_report_generation_and_bilingual_delivery
post_action_confirmation=delivery_manifest_and_independent_receipt
```

## User interface

The user gives one Weekly Index instruction and receives one consolidated project status. The user does not separately coordinate implementation and assurance roles.

## Product boundary

The governance standard applies to both repository tracks when work is consequential:

- Weekly Indices Review — active production product;
- AEX Weekly Options — parked but preserved track.

The hard gate implemented here applies only to the active Weekly Indices Review. It does not merge the two product tracks or grant authority over AEX option execution.

## Enforced pre-send assurance

The production delivery path now defers English transport until the Dutch companion and all bilingual evidence exist. The later bilingual entrypoint reconstructs and validates one release-assurance record before releasing both preserved transport implementations.

The assurance binds source/run/date/token identity, benchmark/proxy pricing evidence, runtime source files, portfolio and valuation state, recommendation scorecard, ranking and coverage artifacts, English and Dutch Markdown/HTML/PDF/equity-curve assets, section parity, financial numeric parity, the English deferral marker, and exact SHA-256 identities.

A failed record prevents both English and Dutch transport.

The hard gate is implemented by:

- `control/INDEX_RELEASE_ASSURANCE_CONTRACT_V1.md`
- `tools/index_release_assurance.py`
- `send_index_report_tv_analyst_distinct.py`
- `send_index_report_bilingual.py`
- `tests/test_index_release_assurance.py`
- `.github/workflows/validate-index-release-assurance.yml`

## Remaining LEVEL 4 boundary

The project remains below LEVEL 4 until the bilingual delivery manifest and independent receiving-system confirmation are bound to the same release identity and hashes. Sequential SMTP success is only `TRANSPORT_SENT_UNVERIFIED`.

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
