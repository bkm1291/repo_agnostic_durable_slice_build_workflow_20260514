#!/usr/bin/env python3
"""Render Markdown entrypoints from the canonical methodology JSON."""

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
from typing import Any, Callable


DEFAULT_METHODOLOGY = "repo_agnostic_durable_slice_build_workflow_methodology_20260514.json"
GENERATED_HEADER = (
    "<!-- GENERATED FROM repo_agnostic_durable_slice_build_workflow_methodology_20260514.json "
    "BY scripts/render_canonical_entrypoints.py. EDIT THE JSON, THEN RUN --write. -->"
)


def _load_methodology(root: Path, methodology_path: str) -> dict[str, Any]:
    path = root / methodology_path
    return json.loads(path.read_text(encoding="utf-8"))


def _wrap_code(value: str) -> str:
    return f"`{value}`"


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _numbered_list(items: list[str]) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def _principle_bullets(methodology: dict[str, Any], limit: int | None = None) -> str:
    principles = methodology.get("non_negotiable_principles", [])
    if limit is not None:
        principles = principles[:limit]
    return "\n".join(
        f"- `{item['principle_id']}`: {item['rule']}" for item in principles
    )


def _starter_artifacts(methodology: dict[str, Any]) -> dict[str, Any]:
    return methodology.get("starter_kit_artifacts", {})


def render_readme(methodology: dict[str, Any]) -> str:
    starter = _starter_artifacts(methodology)
    low_token = starter.get("low_token_workflow", {})
    repo_file_index = starter.get("repo_file_index", {})
    read_only_harness = starter.get("read_only_command_harness", {})
    realistic_example = starter.get("realistic_small_example", {})
    starter_validator_path = starter.get("starter_validator", {}).get(
        "path", "scripts/validate_slice_packet.py"
    )
    local_bootstrap_path = starter.get("local_bootstrap", {}).get(
        "path", "scripts/bootstrap_local_repo.py"
    )
    minimal_example_root = starter.get("minimal_example", {}).get(
        "root", "examples/minimal_repo"
    )
    realistic_example_root = realistic_example.get(
        "root", "examples/small_config_tool_repo"
    )
    workflow = methodology.get("one_page_summary", {}).get("workflow", [])
    quickstart = [
        (
            "Run `python scripts/bootstrap_local_repo.py "
            "../my-new-repo --project-name my-new-repo`."
        ),
        "Change into the generated repo.",
        (
            "Keep the methodology JSON as canonical, or deliberately replace it "
            "with the target repo's canonical methodology file."
        ),
        (
            "Run `python scripts/validate_low_token_workflow.py --summary-only` "
            "to confirm compact-read defaults."
        ),
        (
            "Run `python scripts/build_repo_file_index.py --summary-only` "
            "to preview exact-path read routing without writing an index."
        ),
        (
            "Create `plans/repo_roadmap.json` and "
            "`plans/slices/slice_001_packet.json`."
        ),
        (
            "Run `python scripts/validate_slice_packet.py "
            "plans/slices/slice_001_packet.json --summary-only`."
        ),
        "Fix packet failures before implementation.",
        "Implement only the owner files named in the packet.",
        "Run the owning validator and focused tests.",
        "Commit implementation first.",
        "Refresh generated indexes only if the packet's refresh decision requires it.",
    ]
    canonical_files = [
        (
            "Full methodology: "
            f"{_wrap_code(starter.get('canonical_source', DEFAULT_METHODOLOGY))}"
        ),
        f"Agent entrypoint: {_wrap_code('AGENTS.md')}",
        f"Skill pointer: {_wrap_code('SKILL.md')}",
        f"Prompt library: {_wrap_code('BUILD_STAGE_PROMPTS.md')}",
        f"Starter schemas: {_wrap_code('schemas/')}",
        f"Starter validator: {_wrap_code(starter_validator_path)}",
        f"Low-token contract: {_wrap_code(low_token.get('contract', 'contracts/low_token_workflow_contract.json'))}",
        f"Low-token validator: {_wrap_code(low_token.get('validator', 'scripts/validate_low_token_workflow.py'))}",
        f"Repo file index builder: {_wrap_code(repo_file_index.get('builder', 'scripts/build_repo_file_index.py'))}",
        f"Repo file index query: {_wrap_code(repo_file_index.get('query', 'scripts/query_repo_file_index.py'))}",
        f"Read-only command harness: {_wrap_code(read_only_harness.get('validator', 'scripts/validate_read_only_commands.py'))}",
        f"Read-only command contract: {_wrap_code(read_only_harness.get('contract', 'contracts/read_only_command_harness.json'))}",
        f"Local bootstrap: {_wrap_code(local_bootstrap_path)}",
        f"Minimal example: {_wrap_code(minimal_example_root)}",
        f"Realistic small example: {_wrap_code(realistic_example_root)}",
    ]
    return f"""{GENERATED_HEADER}

# Durable Slice Build Workflow Template

{methodology["positioning_statement"]}

{methodology["purpose"]}

The canonical doctrine is `{starter.get("canonical_source", DEFAULT_METHODOLOGY)}`.
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

{_bullet_list(methodology["not_intended_for"])}

## 10-Minute Bootstrap Path

{_numbered_list(quickstart)}

## Workflow Chain

{_bullet_list(workflow)}

## Low-Token Defaults

Use `{low_token.get("contract", "contracts/low_token_workflow_contract.json")}` as the generic low-token policy. It keeps work index-first, targeted, and compact: query or file-inventory before large reads, normally read no more than 120 lines around exact keys, avoid full reads of giant logs/registries/generated indexes, and prefer `--summary-only` or equivalent compact output.

Validate it with:

```bash
{low_token.get("command_template", "python scripts/validate_low_token_workflow.py --summary-only")}
{repo_file_index.get("summary_command", "python scripts/build_repo_file_index.py --summary-only")}
{read_only_harness.get("summary_command", "python scripts/validate_read_only_commands.py --summary-only")}
```

## Local Reuse

Bootstrap a new local repo:

```bash
python scripts/bootstrap_local_repo.py ../my-new-repo --project-name my-new-repo
cd ../my-new-repo
python scripts/render_canonical_entrypoints.py --check
python scripts/validate_low_token_workflow.py --summary-only
python scripts/build_repo_file_index.py --summary-only
python scripts/validate_read_only_commands.py --summary-only
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
generated entrypoint drift checks, semantic packet validation, a file inventory
builder/query pair, a read-only command harness, and example tests.

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
- `{realistic_example_root}/`:
  realistic config-owned CLI slice with runtime code, config validation, focused
  tests, and a non-skip refresh decision.

## Canonical Files

{_bullet_list(canonical_files)}
"""


def render_agents(methodology: dict[str, Any]) -> str:
    starter = _starter_artifacts(methodology)
    low_token = starter.get("low_token_workflow", {})
    repo_file_index = starter.get("repo_file_index", {})
    read_only_harness = starter.get("read_only_command_harness", {})
    start_steps = [
        "Read this `AGENTS.md`.",
        "Read root `SKILL.md` if present.",
        "Read the canonical methodology JSON.",
        f"Read `{low_token.get('contract', 'contracts/low_token_workflow_contract.json')}` if present.",
        "Check worktree state.",
        "Read the current durable roadmap or owner plan.",
        "Confirm or create the selected slice packet before protected edits.",
        (
            "Classify stale generated outputs as evidence unless a required "
            "validator/test or hard safety invariant fails."
        ),
    ]
    return f"""{GENERATED_HEADER}

# Brand-New Repo Bootstrap Agent Rules

This file is a repo-agnostic bootstrap template for brand-new repositories. Copy
and adapt it into a new repo at creation time. Do not silently override a mature
repo's local authority surfaces.

Canonical doctrine lives in `{starter.get("canonical_source", DEFAULT_METHODOLOGY)}`.
This file is a generated operational entrypoint.

## Repository Identity

Replace this section when bootstrapping the new repo. Treat sibling repos,
archives, downloads, vendor folders, and donor/reference libraries as read-only
unless the current task explicitly authorizes mutation.

## Required Start

{_numbered_list(start_steps)}

## Core Rules

{_principle_bullets(methodology)}

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

Use `{low_token.get("contract", "contracts/low_token_workflow_contract.json")}` as the portable low-token policy. Query an authority map, repo index, file inventory, or exact-path search before opening large repo-truth files. In this template, `{repo_file_index.get("builder", "scripts/build_repo_file_index.py")}` and `{repo_file_index.get("query", "scripts/query_repo_file_index.py")}` are the starter exact-path inventory tools. Targeted reads should normally stay at or below 120 lines around exact keys. Do not full-read giant logs, JSONL streams, registries, generated indexes, or broad handoff notes unless debugging that exact file.

If a targeted read is insufficient, state:

`Need wider read because <specific missing fact>. Reading <path> lines <range> only.`

Prefer validators and status commands that support `--summary-only` or another compact read-only mode. Use `{read_only_harness.get("validator", "scripts/validate_read_only_commands.py")}` to validate or run declared read-only checks under before/after file snapshots.

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
"""


def render_skill(methodology: dict[str, Any]) -> str:
    starter = _starter_artifacts(methodology)
    low_token = starter.get("low_token_workflow", {})
    repo_file_index = starter.get("repo_file_index", {})
    read_only_harness = starter.get("read_only_command_harness", {})
    workflow = methodology.get("one_page_summary", {}).get("workflow", [])
    return f"""{GENERATED_HEADER}

# Brand-New Repo Durable Slice Build Skill

Use this workflow to bootstrap a brand-new repository from scratch and then plan,
implement, validate, and close out work through durable slice evidence.

Canonical doctrine lives in `{starter.get("canonical_source", DEFAULT_METHODOLOGY)}`.
This skill is a compact generated pointer.

## Core Workflow

{_numbered_list(workflow)}

## Planning Mode

Use planning mode only when the roadmap, owner surfaces, proof path, source
evidence, or safety boundaries are unclear. Planning outputs should be durable
and structured: roadmap, slice packet, decision record, open question register,
source-read register, or evidence report.

Do not create runtime configs, schemas, source modules, scripts, or tests during
planning unless implementation is explicitly activated.

## Build Mode

Build Mode begins when the selected slice packet is ready. Read targeted owner
files, reuse existing patterns, keep runtime values config-owned, avoid future
placeholders, add/update the owning validator, add focused tests, run focused
proof, and stage exact intended paths.

## Low-Token Workflow

Use `{low_token.get("contract", "contracts/low_token_workflow_contract.json")}` as the compact-read policy. Query or inspect file inventory before large reads; the starter tools are `{repo_file_index.get("builder", "scripts/build_repo_file_index.py")}` and `{repo_file_index.get("query", "scripts/query_repo_file_index.py")}`. Keep normal targeted reads at or below 120 lines, avoid full reads of giant logs/registries/generated indexes, and prefer `--summary-only` or equivalent compact output. Use `{read_only_harness.get("validator", "scripts/validate_read_only_commands.py")}` when you need command status proof to be read-only.

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
"""


def render_prompts(methodology: dict[str, Any]) -> str:
    prompts = methodology.get("build_stage_prompt_structure", {}).get(
        "self_contained_prompt_templates", {}
    )
    short_prompts = methodology.get("build_stage_prompt_structure", {}).get(
        "short_form_prompt_templates", {}
    )
    starter = _starter_artifacts(methodology)
    prompt_sections = []
    labels = {
        "readiness_prompt_full": "Long Form Readiness Prompt",
        "slice_packet_prompt_full": "Long Form Slice Packet Prompt",
        "implementation_prompt_full": "Long Form Implementation Prompt",
        "focused_proof_prompt_full": "Focused Proof Prompt",
        "generated_refresh_prompt_full": "Generated Refresh Prompt",
        "closeout_prompt_full": "Closeout Prompt",
    }
    for key, title in labels.items():
        value = prompts.get(key)
        if value:
            prompt_sections.append(f"## {title}\n\n```text\n{value}\n```")
    short_sections = []
    for key, value in short_prompts.items():
        if key.endswith("_short"):
            title = key.replace("_", " ").replace("prompt short", "Prompt").title()
            short_sections.append(f"### {title}\n\n```text\n{value}\n```")
    return f"""{GENERATED_HEADER}

# Durable Build Stage Prompts

Use these prompts inside a brand-new repo bootstrapped from this bundle. They are
operator-facing prompt surfaces derived from
`{starter.get("canonical_source", DEFAULT_METHODOLOGY)}`.

Do not use this prompt file to override a mature repo's existing rules.

## Usage Rule

Use long form when starting a new agent, when automatic project-doc injection is
uncertain, or when protected/runtime/source/safety surfaces are involved. Use
short form only when `AGENTS.md`, `SKILL.md`, the durable methodology, and the
active roadmap are already available to the agent.

{"\n\n".join(prompt_sections)}

## Short Form Prompts

{"\n\n".join(short_sections)}
"""


RENDERERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "README.md": render_readme,
    "AGENTS.md": render_agents,
    "SKILL.md": render_skill,
    "BUILD_STAGE_PROMPTS.md": render_prompts,
}


def _normalized(text: str) -> str:
    return text.rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Fail if generated files drift")
    mode.add_argument("--write", action="store_true", help="Rewrite generated entrypoint files")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--methodology", default=DEFAULT_METHODOLOGY)
    args = parser.parse_args()

    root = args.root.resolve()
    methodology = _load_methodology(root, args.methodology)
    drifted: list[str] = []

    for relpath, renderer in RENDERERS.items():
        path = root / relpath
        expected = _normalized(renderer(methodology))
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if args.write:
            path.write_text(expected, encoding="utf-8")
            continue
        if _normalized(current) != expected:
            drifted.append(relpath)
            diff = difflib.unified_diff(
                current.splitlines(),
                expected.splitlines(),
                fromfile=f"{relpath} current",
                tofile=f"{relpath} expected",
                lineterm="",
            )
            print("\n".join(diff))

    if drifted:
        print(f"FAIL entrypoint_drift files={','.join(drifted)}")
        return 1
    print("PASS entrypoints_match_canonical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
