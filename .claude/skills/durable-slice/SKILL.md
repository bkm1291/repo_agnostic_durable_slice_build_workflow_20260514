---
name: durable-slice
description: Start or continue the durable slice workflow in this repo. Use when the user gives a project goal, asks for a roadmap, plans a slice, implements a slice, validates work, or hands work to Claude Code.
argument-hint: "[project goal or slice request]"
---

# Durable Slice Workflow

Use this skill to move from project goal to durable repo evidence without relying
on chat memory.

## Missing Goal Gate

Check `PROJECT_GOAL.md` first. If it exists and contains a concrete
non-placeholder goal, use it automatically.

If `$ARGUMENTS` is empty, only says "use this", only says "use this template",
still contains a placeholder goal, or `PROJECT_GOAL.md` is missing or
placeholder-only, ask exactly:

```text
What do you want to build? One or two paragraphs is enough.
```

Do not create or update a roadmap, packet, or code until the goal is known.

## Startup

1. Read `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `README.md`, and `START_HERE.md`.
2. Read `PROJECT_GOAL.md` if it exists and use it if it contains a real non-placeholder goal.
3. Read `plans/repo_roadmap.json` and the selected `plans/slices/*_packet.json` if they exist.
4. If no roadmap or packet exists, create `plans/repo_roadmap.json` and `plans/slices/slice_001_packet.json` before implementation.
5. Run compact discovery before broad reads:

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

If the current task only created or updated the roadmap and first slice packet,
stop after the packet validates. Report that the packet is ready and do not
create app/source implementation files unless the current user request
explicitly activates implementation.

After an implementation slice passes proof, close out the slice and report the
next governed action from the roadmap. The next slice still requires a valid
packet before implementation. Do not turn closeout into generated operator
prompt text after the initial setup prompt.
