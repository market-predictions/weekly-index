# Weekly Index OS — Project Bootstrap

## Purpose

This is the stable bootstrap file for the ChatGPT Project that works with `market-predictions/weekly-index`.

The ChatGPT Project is the workbench. GitHub is the live source of truth for control files, prompts, scripts, workflows, state, reports, and delivery evidence.

## Read order for serious work

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. `control/PROJECT_GOVERNANCE_BOOTSTRAP.md` for consequential work
5. only then the minimum relevant execution files

## Product tracks

The repository contains two distinct tracks:

- **Weekly Indices Review** — active production report product;
- **AEX Weekly Options** — parked but preserved options-native track.

Do not merge their decision frameworks, input/state contracts, output contracts, or operational runbooks.

## Separation of duties

The project uses one user-facing coordinator and two internally separated roles:

```text
implementation_operations
governance_release_assurance
```

The user gives one instruction and receives one consolidated project status. The user does not separately coordinate the two roles.

Implementation prepares the candidate. Governance independently reconstructs and certifies or rejects it. Implementation may not certify its own completion. Governance may not silently modify the candidate it reviews. A repaired candidate receives a new assurance pass.

The shared standard, local risk class, adoption maturity, and required evidence are linked from `control/PROJECT_GOVERNANCE_BOOTSTRAP.md`.

## Required architecture distinctions

Always keep these five layers separate:

1. decision framework
2. input/state contract
3. output contract
4. operational runbook
5. governance and release assurance

## Weekly Indices Review execution paths

- report logic: `index.txt`, `index-pro.txt`, and `prompts/weekly_indices/`
- pricing and research: `pricing_indices/`, `research_indices/`
- rendering and delivery: `send_index_report.py`, `send_index_report_tv.py`
- orchestration: `.github/workflows/send-weekly-indices-report.yml`
- state and outputs: `output_indices/`

## AEX Weekly Options execution paths

Use the AEX-specific prompts, snapshot builders, trade-plan validator, send script, workflows, and `output_aex/` only when that parked track is explicitly in scope.

## Guardrails

- Benchmark-index and tradable-proxy prices are not interchangeable.
- Technicals are confirmation, not the whole decision engine.
- Do not collapse the architecture into one monolith.
- Do not let Dutch output run a second investment model.
- Treat generated output as a release candidate until the required assurance pass exists.
- Do not claim delivery from rendering, workflow invocation, or SMTP acceptance alone.
- Report action execution separately from independently confirmed outcome.

## Minimal upload strategy

Upload this bootstrap file as stable ChatGPT Project context. Read changing files live from GitHub rather than uploading them as permanent project files.

## Session close rule

After meaningful work, assess updates to:

- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`
- `changelog.md`
- project governance and assurance files

## One-line reminder

**Use one project instruction, two internally separated roles, and GitHub evidence as the authority for completion.**
