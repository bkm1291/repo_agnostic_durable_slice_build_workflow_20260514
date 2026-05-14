<!-- GENERATED FROM repo_agnostic_durable_slice_build_workflow_methodology_20260514.json BY scripts/render_canonical_entrypoints.py. EDIT THE JSON, THEN RUN --write. -->

# Durable Slice Build Workflow Template

This is not a coding template. It is a build-governance template for working with AI agents.

Capture a reusable from-scratch planning and implementation workflow for building new complex repositories through durable evidence, small provable slices, focused validators, future-facing notes, conditional index refreshes, and meaningful closeout receipts.

The canonical doctrine is `repo_agnostic_durable_slice_build_workflow_methodology_20260514.json`.
Markdown entrypoints are generated summaries; edit the JSON and run:

```bash
python scripts/render_canonical_entrypoints.py --write
```

## Use This When

- You are creating a brand-new repo from scratch.
- You want future workers to recover project state without chat history.
- You want each implementation slice to name owner files, proof, tests, refresh
  decisions, and closeout criteria before coding.
- You need generated indexes, receipts, checkpoints, or reports to stay meaningful.

## Do Not Use This When

- silently overriding an existing repo's AGENTS.md, SKILL.md, pyproject.toml, roadmap, indexes, validators, or safety policies
- retroactively replacing a mature repo's local authority without an explicit migration plan
- copying one repo's exact commands, paths, indexes, providers, or safety rules into another repo without adaptation

## 10-Minute Bootstrap Path

1. Run `python scripts/bootstrap_local_repo.py ../my-new-repo --project-name my-new-repo`.
2. Change into the generated repo.
3. Keep the methodology JSON as canonical, or deliberately replace it with the target repo's canonical methodology file.
4. Create `plans/repo_roadmap.json` and `plans/slices/slice_001_packet.json`.
5. Run `python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only`.
6. Fix packet failures before implementation.
7. Implement only the owner files named in the packet.
8. Run the owning validator and focused tests.
9. Commit implementation first.
10. Refresh generated indexes only if the packet's refresh decision requires it.

## Workflow Chain

- Durable roadmap
- Per-slice packet
- Owner files
- Owner validator
- Focused tests
- Future notes
- Conditional generated/index refresh
- Closeout receipt only when it proves something

## Local Reuse

Bootstrap a new local repo:

```bash
python scripts/bootstrap_local_repo.py ../my-new-repo --project-name my-new-repo
cd ../my-new-repo
python scripts/render_canonical_entrypoints.py --check
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
python -m pytest -q tests
```

The bootstrap command refuses to overwrite existing files unless `--force` is
explicit. Examples are copied by default; use `--no-examples` for a lean starter.

## Publish-Ready Checks

Before publishing or pushing a release branch:

```bash
make check
git status --short
```

The template includes `LICENSE`, `CHANGELOG.md`, `.gitattributes`, `.gitignore`,
generated entrypoint drift checks, semantic packet validation, and example tests.

## First Slice Readiness

A slice is ready when its packet names the selected slice, files to create or edit,
owner configs/schemas/contracts, required source reads, owning validator, focused
tests, not-in-scope boundaries, refresh decision, and commit plan.

If any of those are vague, split the slice or return to targeted planning.

## Proof Before Closeout

```bash
python -m json.tool plans/slices/slice_001_packet.json >/dev/null
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
python -m pytest -q tests
git diff --check
git status --short
```

Adjust commands to the target repo's language and test runner.

## Examples

- `examples/minimal_repo/`: smallest packet-validator loop.
- `examples/small_config_tool_repo/`:
  realistic config-owned CLI slice with runtime code, config validation, focused
  tests, and a non-skip refresh decision.

## Canonical Files

- Full methodology: `repo_agnostic_durable_slice_build_workflow_methodology_20260514.json`
- Agent entrypoint: `AGENTS.md`
- Skill pointer: `SKILL.md`
- Prompt library: `BUILD_STAGE_PROMPTS.md`
- Starter schemas: `schemas/`
- Starter validator: `scripts/validate_slice_packet.py`
- Local bootstrap: `scripts/bootstrap_local_repo.py`
- Minimal example: `examples/minimal_repo`
- Realistic small example: `examples/small_config_tool_repo`
