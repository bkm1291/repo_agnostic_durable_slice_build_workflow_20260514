---
name: durable-slice
description: Start or continue the durable slice workflow in this repo. Use when the user gives a project goal, asks for a roadmap, plans a slice, implements a slice, validates work, or hands work to Claude Code.
argument-hint: "[project goal or slice request]"
---

# Durable Slice Workflow

Use this skill to move from project goal to durable repo evidence without relying
on chat memory.

## Startup

1. Read `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `README.md`, and `START_HERE.md`.
2. Read `plans/repo_roadmap.json` and the selected `plans/slices/*_packet.json` if they exist.
3. If no roadmap or packet exists, create `plans/repo_roadmap.json` and `plans/slices/slice_001_packet.json` before implementation.
4. Run compact discovery before broad reads:

```bash
python scripts/build_repo_file_index.py --summary-only
python scripts/build_command_map.py --summary-only
python scripts/query_command_map.py --safe-read-only --summary-only
```

## Packet Before Code

Before editing source files, make the selected packet name:

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

Validate it:

```bash
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
```

If validation fails, fix the packet before implementation.

## Build

- Edit only files listed in `files_to_create_or_edit`.
- If ownership changes, update and revalidate the packet before continuing.
- Keep runtime-affecting values in config, schema, contract, policy, or explicit operator selection.
- Add or update the owning validator and focused tests named in the packet.
- Keep future work in `not_in_scope` and `boundary_rules` unless this slice explicitly owns it.

## Validation

Run the packet's focused commands, then run the compact repo checks that apply:

```bash
python scripts/render_canonical_entrypoints.py --check
python scripts/validate_low_token_workflow.py --summary-only
python scripts/validate_source_read_register.py --summary-only
python scripts/validate_planned_future_surfaces.py --summary-only
python scripts/validate_claude_integration.py --summary-only
python scripts/validate_read_only_commands.py --summary-only
python scripts/validate_release_package.py --summary-only
python -m pytest -q tests
git diff --check
git status --short
```

## Closeout

Report changed files, validation commands and results, generated-refresh decision,
worktree state, remaining risks, and the next recommended slice. Do not leave
future requirements only in chat.
