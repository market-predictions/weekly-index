# Decision — Adopt Two-Role Governance for Weekly Index

## Date

2026-08-05

## Decision

Adopt `CROSS_PROJECT_TWO_ROLE_GOVERNANCE_V1` for consequential Weekly Index and AEX Weekly Options work while preserving the two product tracks as separate architectures.

The user continues to issue one instruction. Internally:

- `implementation_operations` prepares the candidate;
- `governance_release_assurance` independently reconstructs and certifies or rejects it.

Implementation cannot certify its own completion. Governance cannot silently modify the candidate it reviews.

## Current maturity

```text
current=LEVEL_1_CHECKLIST
target=LEVEL_4_POST_ACTION_INDEPENDENT_CONFIRMATION
```

## Required follow-up

Create `control/INDEX_RELEASE_ASSURANCE_CONTRACT_V1.md`, machine-readable assurance evidence, a hard pre-send gate for production delivery, and independent post-delivery confirmation.

The contract must preserve benchmark-index versus tradable-proxy separation and bilingual parity.

## Authority boundary

This decision does not authorize report generation, portfolio mutation, option trade-plan execution, workflow dispatch, or email delivery.
