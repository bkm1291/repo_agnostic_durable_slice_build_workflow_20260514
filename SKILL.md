<!-- GENERATED FROM repo_agnostic_durable_slice_build_workflow_methodology_20260514.json BY scripts/render_canonical_entrypoints.py. EDIT THE JSON, THEN RUN --write. -->

# Brand-New Repo Durable Slice Build Skill

Use this workflow to bootstrap a brand-new repository from scratch and then plan,
implement, validate, and close out work through durable slice evidence.

Canonical doctrine lives in `repo_agnostic_durable_slice_build_workflow_methodology_20260514.json`.
This skill is a compact generated pointer.

## Project Goal Intake

Check `PROJECT_GOAL.md` first. If it exists and contains a concrete non-placeholder goal, use it automatically. If the user says only "use this", "use this template", gives a placeholder goal, or `PROJECT_GOAL.md` is missing/placeholder-only, ask exactly: "What do you want to build? One or two paragraphs is enough." Do not create or update a roadmap, packet, or code until the goal is known.

## Core Workflow

1. Durable roadmap
2. Per-slice packet
3. Owner files
4. Owner validator
5. Focused tests
6. Future notes
7. Conditional generated/index refresh
8. Closeout receipt only when it proves something

## Planning Mode

Use planning mode only when the roadmap, owner surfaces, proof path, source
evidence, or safety boundaries are unclear. Planning outputs should be durable
and structured: roadmap, slice packet, decision record, open question register,
source-read register, planned-future-surfaces registry, or evidence report.

Do not create runtime configs, schemas, source modules, scripts, or tests during
planning unless implementation is explicitly activated.

## Build Mode

Build Mode begins when the selected slice packet is ready. Read targeted owner
files, reuse existing patterns, keep runtime values config-owned, avoid future
placeholders, enforce `boundary_rules`, add/update the owning validator, add
focused tests, run focused proof, and stage exact intended paths.

## Low-Token Workflow

Use `contracts/low_token_workflow_contract.json` as the compact-read policy. Query or inspect file inventory before large reads; the starter tools are `scripts/build_repo_file_index.py` and `scripts/query_repo_file_index.py`. Keep normal targeted reads at or below 120 lines, avoid full reads of giant logs/registries/generated indexes, and prefer `--summary-only` or equivalent compact output. Use `scripts/validate_read_only_commands.py` when you need command status proof to be read-only.

Use `plans/source_read_register.json` for durable source/full-read refs and `plans/planned_future_surfaces.json` for intentionally deferred future files.

Use `scripts/build_command_map.py`, `scripts/query_command_map.py`, and `scripts/validate_command_map.py` before adding new command, helper, validator, builder, writer, or test surfaces.

For mature repos, validate an explicit migration packet with `scripts/validate_mature_repo_migration_packet.py` before copying or adapting template files.

If a wider read is needed, state:

`Need wider read because <specific missing fact>. Reading <path> lines <range> only.`

## Packet Checklist

- `selected_wave_or_slice`
- `files_to_create_or_edit`
- `exact_owner_configs_schemas_contracts`
- `required_source_reads`
- `owning_wave_validator`
- `owning_wave_tests`
- `focused_validators_and_tests`
- `not_in_scope`
- `boundary_rules`
- `refresh_decision`
- `commit_plan`

## Focused Proof

```bash
python -m json.tool <changed-json> >/dev/null
python <owning-validator> --summary-only
python -m pytest -q <focused-tests>
git diff --check
git status --short
```

## Refresh And Receipts

Generated indexes refresh only when the packet requires them. Receipts and
checkpoints are for writers, generators, materializers, external actions,
irreversible operations, and closeout gates, not default status notes.
