<!-- GENERATED FROM repo_agnostic_durable_slice_build_workflow_methodology_20260514.json BY scripts/render_canonical_entrypoints.py. EDIT THE JSON, THEN RUN --write. -->

# Durable Slice Build Workflow Template

## What This Is

This is not a coding template. It is a build-governance template for working with AI agents.

Capture a reusable from-scratch planning and implementation workflow for building new complex repositories through durable evidence, small provable slices, focused validators, future-facing notes, conditional index refreshes, and meaningful closeout receipts.

## New Here? Start With `START_HERE.md`

Easiest path:

1. Drag this folder into Claude Code or Codex.
2. Paste this:

```text
Read this folder and use it as the workflow template for my repo.

I authorize you to inspect the files in this folder.

If I name a target repo path or folder, I authorize you to create that folder if needed, copy or bootstrap this workflow into it, and create or update only the starter roadmap and first slice packet before coding. If I say current repo, current folder, current one, or you are already working inside an empty target folder, use the current working directory as the target. If no target repo path or folder is clear, ask me for it before writing files.

First read README.md, START_HERE.md, AGENTS.md, and `PROJECT_GOAL.md` if it exists. If `PROJECT_GOAL.md` has a real non-placeholder goal, use it automatically. If it is missing or still placeholder text, ask me exactly: "What do you want to build? One or two paragraphs is enough."

After the goal is known, create or update the roadmap and first slice packet, then validate the packet. Do not create app/source implementation files or code features until the packet validates. Do not code until the packet validates. This first prompt establishes build governance; after that, keep the work in this same conversation, reason from repo-native artifacts, and follow the roadmap/slice/validator/test structure without turning closeout into generated prompt text.
```

3. If the agent asks what you want to build, answer in one or two paragraphs.
4. The agent should create or update the roadmap and first slice packet, validate
   the packet, and wait to code until the packet passes.
5. After that, the repo artifacts carry the workflow. The agent should follow
   the governed structure in the same thread without producing recurring
   operator prompt instructions.

No-prompt option: copy `PROJECT_GOAL.template.md` to `PROJECT_GOAL.md`, fill
in the goal, then drag this folder into Claude Code or Codex and paste the same
instruction above. The agent will read the goal automatically.

Short fallback if the agent already knows it can read the folder:

```text
Read this folder and use its workflow template. Do not code until the first slice packet validates.
```

If this workflow is new to you, start with `START_HERE.md`. It gives the shortest path: bootstrap a repo, run starter checks, read the roadmap and first slice packet, edit the packet before code, prove the slice, and commit.

## Giving This To An Agent? Use `PROMPT_FOR_NEW_AGENT.md`

Fill in `PROMPT_FOR_NEW_AGENT.md` with the repo path, project goal, and smallest next slice, then paste it into a fresh agent. That prompt tells the agent what to read first, how to stay inside the repo, how to validate, and how to close out without leaving important decisions only in chat.

Using Claude Code? `CLAUDE.md` is the always-loaded entrypoint. Run `/skills` to confirm the project skills are available, then start with `/durable-slice <project goal or slice request>`.

Use `RELEASE_CHECKLIST.md` before tagging or publishing, `docs/CI.md` for CI expectations, `docs/MIGRATING_MATURE_REPO.md` before adopting this template into an existing repo, `docs/GLOSSARY.md` for terms, `docs/TROUBLESHOOTING.md` for validator failures, `docs/NEXT_ACTION_DECISION_TREE.md` when you do not know the next action, and `docs/ANNOTATED_SLICE_PACKET.md` before writing your first packet.

## 10-Minute Bootstrap Path

1. If you are new to the workflow, read `START_HERE.md` first.
2. To hand the repo to a fresh agent, fill in and paste `PROMPT_FOR_NEW_AGENT.md`.
3. Run `python scripts/bootstrap_local_repo.py ../my-new-repo --project-name my-new-repo`.
4. If you want git/GitHub tracking from the start, include `--init-git` and optional `--github-remote <url>` in the bootstrap.
5. Change into the generated repo.
6. Keep the methodology JSON as canonical, or deliberately replace it with the target repo's canonical methodology file.
7. Run `python scripts/validate_low_token_workflow.py --summary-only` to confirm compact-read defaults.
8. Run `python scripts/validate_source_read_register.py --summary-only` to confirm durable source-read evidence refs.
9. Run `python scripts/validate_planned_future_surfaces.py --summary-only` to confirm intentionally deferred future files are classified.
10. Run `python scripts/build_repo_file_index.py --summary-only` to preview exact-path read routing without writing an index.
11. Run `python scripts/build_command_map.py --summary-only` and `python scripts/validate_command_map.py --summary-only` to confirm command discovery.
12. Run `python scripts/query_command_map.py --safe-read-only --summary-only` to preview safe command routing.
13. Run `python scripts/validate_claude_integration.py --summary-only` to confirm Claude Code entrypoints and skills are present.
14. Create `plans/repo_roadmap.json` and `plans/slices/slice_001_packet.json`.
15. Run `python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only`.
16. Fix packet failures before implementation.
17. Implement only the owner files named in the packet.
18. Run the owning validator and focused tests.
19. Commit implementation first.
20. Refresh generated indexes only if the packet's refresh decision requires it.

## Expert / Custom Path

The canonical doctrine is `repo_agnostic_durable_slice_build_workflow_methodology_20260514.json`.
Markdown entrypoints are generated summaries. For custom methodology changes, edit the JSON and run:

```bash
python scripts/render_canonical_entrypoints.py --write
```

Use `schemas/` for portable JSON shape rules, Python validators for semantic workflow rules, `contracts/` and `plans/` for repo authority, and generated Markdown entrypoints for agent-facing summaries.

Claude Code support stays on the same doctrine: `CLAUDE.md` imports `AGENTS.md`, `.claude/skills/` holds on-demand workflows, and `scripts/validate_claude_integration.py --summary-only` checks that no default hooks, MCP servers, or broad tool pre-approvals were added.

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

## Workflow Chain

- Durable roadmap
- Per-slice packet
- Owner files
- Owner validator
- Focused tests
- Future notes
- Conditional generated/index refresh
- Closeout receipt only when it proves something

## Low-Token Defaults

Use `contracts/low_token_workflow_contract.json` as the generic low-token policy. It keeps work index-first, targeted, and compact: query or file-inventory before large reads, normally read no more than 120 lines around exact keys, avoid full reads of giant logs/registries/generated indexes, and prefer `--summary-only` or equivalent compact output.

Validate it with:

```bash
python scripts/validate_low_token_workflow.py --summary-only
python scripts/validate_source_read_register.py --summary-only
python scripts/validate_planned_future_surfaces.py --summary-only
python scripts/build_repo_file_index.py --summary-only
python scripts/build_command_map.py --summary-only
python scripts/query_command_map.py --safe-read-only --summary-only
python scripts/validate_command_map.py --summary-only
python scripts/validate_read_only_commands.py --summary-only
```

## Local Reuse

Bootstrap a new local repo:

```bash
python scripts/bootstrap_local_repo.py ../my-new-repo --project-name my-new-repo
cd ../my-new-repo
python scripts/render_canonical_entrypoints.py --check
python scripts/validate_low_token_workflow.py --summary-only
python scripts/validate_source_read_register.py --summary-only
python scripts/validate_planned_future_surfaces.py --summary-only
python scripts/build_repo_file_index.py --summary-only
python scripts/build_command_map.py --summary-only
python scripts/query_command_map.py --safe-read-only --summary-only
python scripts/validate_command_map.py --summary-only
python scripts/validate_claude_integration.py --summary-only
python scripts/validate_read_only_commands.py --summary-only
python scripts/validate_release_package.py --summary-only
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
python -m pytest -q tests
```

The bootstrap command refuses to overwrite existing files unless `--force` is
explicit. Examples are copied by default; use `--no-examples` for a lean starter.

## Git And GitHub Tracking

Let people who bootstrap this workflow into a new repo start with traceable git history and optional GitHub remote/CI routing instead of relying on local files or chat state.

The template copy operation does not create .git unless the operator asks for it. When the operator wants systematic tracking, initialize git before implementation, commit bootstrap governance, and push to GitHub only after local validators pass.

For a new repo that should be tracked immediately:

```bash
python scripts/bootstrap_local_repo.py ../my-new-repo --project-name my-new-repo --init-git --github-remote git@github.com:<owner>/<repo>.git
cd ../my-new-repo
git status --short
git push -u origin main
```

Tracking sequence:

- Commit bootstrap entrypoints, roadmap, first packet, validators, tests, and CI as the initial governance commit.
- For each implementation slice, commit owner files, packet or roadmap updates, focused tests, and validator changes as the implementation commit.
- If the slice refresh_decision requires generated discovery, run refresh from the implementation head and create one generated-refresh commit for the generated outputs.
- If a receipt/checkpoint proves a writer, materializer, external action, irreversible decision, release gate, or phase closeout, commit it with that closeout evidence.
- Push to GitHub after local proof passes and confirm GitHub Actions checks before treating the branch as shared authority.

The copied .github/workflows/check.yml is part of the bootstrap governance surface. It should run make check, make bootstrap-smoke, and make read-only-check on push and pull_request before a shared branch or release is considered healthy.

## Publish-Ready Checks

Before publishing or pushing a release branch:

```bash
make check
make bootstrap-smoke
make read-only-check
python scripts/validate_release_package.py --summary-only
git status --short
```

The template includes `LICENSE`, `CHANGELOG.md`, `.gitattributes`, `.gitignore`,
generated entrypoint drift checks, semantic packet validation, a file inventory
builder/query pair, a queryable command map, Claude Code entrypoints/skills, a read-only command harness, release
package validation, and example tests.

Use `RELEASE_CHECKLIST.md` for the full tag and publish sequence.

## Schema Vs Validator Authority

Schemas define JSON shape, required fields, allowed enum values, and portable structural constraints. Python validators define semantic rules, cross-file rules, side-effect rules, read-only checks, and local adoption safety. When a schema accepts a document but the Python validator rejects it, the validator rejection blocks closeout until the schema or document is intentionally updated.

## Mature Repo Adoption

Do not apply this template to an existing mature repo without a migration packet. Read `docs/MIGRATING_MATURE_REPO.md` and validate the packet with `python scripts/validate_mature_repo_migration_packet.py <packet> --summary-only` before copying or adapting template files.

## First Slice Readiness

A slice is ready when its packet names the selected slice, files to create or edit,
owner configs/schemas/contracts, required source reads, owning validator, focused
tests, not-in-scope boundaries, machine-checkable boundary rules, refresh
decision, and commit plan.

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
- Project goal template: `PROJECT_GOAL.template.md`
- Local project goal intake: `PROJECT_GOAL.md`
- Claude Code entrypoint: `CLAUDE.md`
- Claude Code durable-slice skill: `.claude/skills/durable-slice/SKILL.md`
- Claude Code audit skill: `.claude/skills/durable-slice-audit/SKILL.md`
- Claude Code release skill: `.claude/skills/durable-slice-release/SKILL.md`
- Claude Code validator: `scripts/validate_claude_integration.py`
- Starter schemas: `schemas/`
- Starter validator: `scripts/validate_slice_packet.py`
- Low-token contract: `contracts/low_token_workflow_contract.json`
- Low-token validator: `scripts/validate_low_token_workflow.py`
- Repo file index builder: `scripts/build_repo_file_index.py`
- Repo file index query: `scripts/query_repo_file_index.py`
- Command map contract: `contracts/command_map_contract.json`
- Command map builder: `scripts/build_command_map.py`
- Command map query: `scripts/query_command_map.py`
- Command map validator: `scripts/validate_command_map.py`
- Read-only command harness: `scripts/validate_read_only_commands.py`
- Read-only command contract: `contracts/read_only_command_harness.json`
- Source-read register: `plans/source_read_register.json`
- Source-read validator: `scripts/validate_source_read_register.py`
- Planned future surfaces: `plans/planned_future_surfaces.json`
- Planned future validator: `scripts/validate_planned_future_surfaces.py`
- Beginner start: `START_HERE.md`
- New-agent setup prompt: `PROMPT_FOR_NEW_AGENT.md`
- Release checklist: `RELEASE_CHECKLIST.md`
- Release package validator: `scripts/validate_release_package.py`
- CI guide: `docs/CI.md`
- Mature-repo migration guide: `docs/MIGRATING_MATURE_REPO.md`
- Mature-repo migration validator: `scripts/validate_mature_repo_migration_packet.py`
- Glossary: `docs/GLOSSARY.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- Next-action decision tree: `docs/NEXT_ACTION_DECISION_TREE.md`
- Annotated slice packet: `docs/ANNOTATED_SLICE_PACKET.md`
- Local bootstrap: `scripts/bootstrap_local_repo.py`
- Minimal example: `examples/minimal_repo`
- Realistic small example: `examples/small_config_tool_repo`
