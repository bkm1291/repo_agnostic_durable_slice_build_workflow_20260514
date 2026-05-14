<!-- GENERATED FROM repo_agnostic_durable_slice_build_workflow_methodology_20260514.json BY scripts/render_canonical_entrypoints.py. EDIT THE JSON, THEN RUN --write. -->

# Brand-New Repo Bootstrap Agent Rules

This file is a repo-agnostic bootstrap template for brand-new repositories. Copy
and adapt it into a new repo at creation time. Do not silently override a mature
repo's local authority surfaces.

Canonical doctrine lives in `repo_agnostic_durable_slice_build_workflow_methodology_20260514.json`.
This file is a generated operational entrypoint.

## Repository Identity

Replace this section when bootstrapping the new repo. Treat sibling repos,
archives, downloads, vendor folders, and donor/reference libraries as read-only
unless the current task explicitly authorizes mutation.

## Required Start

1. Read this `AGENTS.md`.
2. Read root `SKILL.md` if present.
3. Read the canonical methodology JSON.
4. Read `contracts/low_token_workflow_contract.json` if present.
5. Check worktree state.
6. Read the current durable roadmap or owner plan.
7. Confirm or create the selected slice packet before protected edits.
8. Classify stale generated outputs as evidence unless a required validator/test or hard safety invariant fails.

## Core Rules

- `durability_over_chat`: Important decisions must be saved in repo-native durable artifacts before they are treated as future authority.
- `small_provable_slices`: A slice must be small enough that its owner surfaces, validator, tests, and downstream effects can be named before coding starts.
- `low_token_by_default`: Use index or file-inventory routing before broad reads, keep targeted reads normally at or below 120 lines, and make command output compact by default.
- `owner_validator_first`: Every implementation slice must have an owning validator or explicitly extend an existing owning validator.
- `focused_tests_are_slice_proof`: Focused tests prove the behavior added by the slice. Broad index or status checks are navigation evidence, not behavioral proof.
- `future_notes_only_when_actionable`: Only save future-wave notes when a discovery changes future implementation order, owner files, validators, full-read/source requirements, safety boundaries, index requirements, activation gates, or closeout criteria.
- `conditional_generated_refresh`: Generated indexes, catalogs, inventories, projections, dashboards, and receipts refresh only when the selected slice owns them, future discovery depends on them, stale discovery blocks work, closeout requires them, or the operator explicitly requests them.
- `receipts_are_not_status_confetti`: Do not write receipts or checkpoints merely to say work happened. Write them when they prove an output writer, materializer, generator, external action, closeout gate, or irreversible decision.
- `implementation_before_generated_refresh`: Commit implementation first, then refresh generated discovery outputs if required, then commit generated outputs separately once.
- `no_head_chasing`: After a generated-index commit, do not run another refresh only because the generated index describes its parent commit.
- `config_owns_runtime_values`: Runtime-affecting values belong in config, policy, contract, schema, or explicit operator selection, not hidden in code or chat.

## Slice Readiness Guard

Before implementation, answer:

- What owns this behavior?
- What proves it?
- What can fail?
- What future slice depends on it?
- What belongs in config or explicit operator selection?
- What is evidence and what is authority?
- What should not be built yet?
- What generated output is useful versus noise?

If the answers are vague, split the slice or return to targeted planning.

## Build Mode

Implement only the owner bundle named in the packet. Use existing helpers,
indexes, catalogs, and patterns before creating new helpers. Keep reads targeted
and command output compact under the low-token contract. Keep runtime values
config-owned or explicitly operator-selected.

## Low-Token Workflow

Use `contracts/low_token_workflow_contract.json` as the portable low-token policy. Query an authority map, repo index, file inventory, or exact-path search before opening large repo-truth files. Targeted reads should normally stay at or below 120 lines around exact keys. Do not full-read giant logs, JSONL streams, registries, generated indexes, or broad handoff notes unless debugging that exact file.

If a targeted read is insufficient, state:

`Need wider read because <specific missing fact>. Reading <path> lines <range> only.`

Prefer validators and status commands that support `--summary-only` or another compact read-only mode.

## Generated Outputs

Generated indexes, catalogs, inventories, projections, dashboards, and receipts
refresh only when the structured refresh decision requires them. Commit
implementation first, generated refresh second, and do not chase head-only
staleness.

## Safety

Do not persist secrets, tokenized URLs, credential values, private endpoint URLs,
or copied proprietary source unless the repo has an explicit licensed-source
policy. Do not mutate donor repos, vendor repos, or external data roots unless
the task explicitly authorizes it. Do not weaken tests to make a change pass.

## Closeout

Report implementation commit, generated-refresh commit if any, validation
commands/results, worktree state, classified residual noise, future-affecting
notes persisted, and whether the next wave is ready.
