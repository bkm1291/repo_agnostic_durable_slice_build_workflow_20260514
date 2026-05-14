#!/usr/bin/env python3
"""Bootstrap a new local repo from this durable slice workflow template."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METHODOLOGY = "repo_agnostic_durable_slice_build_workflow_methodology_20260514.json"

CORE_PATHS = (
    ".gitignore",
    ".gitattributes",
    "LICENSE",
    "CHANGELOG.md",
    "PROMPT_FOR_NEW_AGENT.md",
    "RELEASE_CHECKLIST.md",
    "START_HERE.md",
    "Makefile",
    "README.md",
    "AGENTS.md",
    "SKILL.md",
    "BUILD_STAGE_PROMPTS.md",
    "pyproject.toml",
    METHODOLOGY,
    "docs",
    "contracts",
    "plans",
    "schemas",
    "scripts",
    "tests",
)

EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache"}


def slugify_project_name(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug or "new-durable-slice-repo"


def _iter_source_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files: list[Path] = []
    for item in sorted(path.rglob("*")):
        if any(part in EXCLUDED_DIRS for part in item.parts):
            continue
        if item.is_file():
            files.append(item)
    return files


def _copy_file(src: Path, dst: Path, project_name: str) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8")
    if src.name == "pyproject.toml":
        text = re.sub(
            r'^name = "[^"]+"$',
            f'name = "{slugify_project_name(project_name)}"',
            text,
            count=1,
            flags=re.MULTILINE,
        )
        text = re.sub(
            r'^description = ".*"$',
            f'description = "Durable slice workflow bootstrap for {project_name}."',
            text,
            count=1,
            flags=re.MULTILINE,
        )
    dst.write_text(text, encoding="utf-8")


def _planned_outputs(
    target: Path, include_examples: bool, include_starter_plan: bool
) -> list[tuple[Path, Path | None]]:
    planned: list[tuple[Path, Path | None]] = []
    paths = list(CORE_PATHS)
    if include_examples:
        paths.append("examples")
    for rel in paths:
        src = ROOT / rel
        for file_path in _iter_source_files(src):
            planned.append((target / file_path.relative_to(ROOT), file_path))
    if include_starter_plan:
        planned.extend(
            [
                (target / "plans" / "repo_roadmap.json", None),
                (target / "plans" / "slices" / "slice_001_packet.json", None),
            ]
        )
    return planned


def _starter_roadmap(project_name: str) -> dict:
    return {
        "roadmap_id": f"{slugify_project_name(project_name).replace('-', '_')}_roadmap",
        "status": "active",
        "purpose": f"Bootstrap {project_name} with the durable slice workflow.",
        "waves": [
            {
                "wave_id": "slice_001",
                "goal": (
                    "Verify the copied workflow entrypoints, packet validator, "
                    "and focused tests."
                ),
                "packet": "plans/slices/slice_001_packet.json",
                "status": "implementation_ready",
                "owner_area": "workflow_bootstrap",
                "depends_on": [],
                "not_in_scope": [
                "Domain runtime implementation",
                "Generated index refresh",
                "External source access",
                ],
            }
        ],
        "validation_policy": {
            "commands": [
                "python scripts/render_canonical_entrypoints.py --check",
                "python scripts/validate_low_token_workflow.py --summary-only",
                "python scripts/build_repo_file_index.py --summary-only",
                "python scripts/validate_read_only_commands.py --summary-only",
                (
                    "python scripts/validate_slice_packet.py "
                    "plans/slices/slice_001_packet.json --summary-only"
                ),
                "python -m pytest -q tests",
            ]
        },
    }


def _starter_packet() -> dict:
    return {
        "selected_wave_or_slice": "slice_001",
        "goal": "Verify the copied durable slice workflow starter surfaces.",
        "files_to_create_or_edit": [
            "README.md",
            "START_HERE.md",
            "PROMPT_FOR_NEW_AGENT.md",
            "RELEASE_CHECKLIST.md",
            "docs/GLOSSARY.md",
            "docs/MIGRATING_MATURE_REPO.md",
            "docs/TROUBLESHOOTING.md",
            "docs/NEXT_ACTION_DECISION_TREE.md",
            "docs/ANNOTATED_SLICE_PACKET.md",
            "AGENTS.md",
            "SKILL.md",
            "BUILD_STAGE_PROMPTS.md",
            "pyproject.toml",
            METHODOLOGY,
            "schemas/methodology.schema.json",
            "schemas/slice_packet.schema.json",
            "schemas/refresh_decision.schema.json",
            "schemas/low_token_workflow_contract.schema.json",
            "schemas/repo_file_index.schema.json",
            "schemas/command_map.schema.json",
            "schemas/mature_repo_migration_packet.schema.json",
            "schemas/read_only_command_harness.schema.json",
            "schemas/source_read_register.schema.json",
            "schemas/planned_future_surfaces.schema.json",
            "contracts/command_map_contract.json",
            "contracts/low_token_workflow_contract.json",
            "contracts/read_only_command_harness.json",
            "plans/source_read_register.json",
            "plans/planned_future_surfaces.json",
            "scripts/build_repo_file_index.py",
            "scripts/build_command_map.py",
            "scripts/query_repo_file_index.py",
            "scripts/render_canonical_entrypoints.py",
            "scripts/validate_command_map.py",
            "scripts/validate_mature_repo_migration_packet.py",
            "scripts/validate_read_only_commands.py",
            "scripts/validate_low_token_workflow.py",
            "scripts/validate_source_read_register.py",
            "scripts/validate_planned_future_surfaces.py",
            "scripts/validate_slice_packet.py",
            "tests/test_repo_file_index.py",
            "tests/test_command_map.py",
            "tests/test_validate_mature_repo_migration_packet.py",
            "tests/test_validate_read_only_commands.py",
            "tests/test_render_canonical_entrypoints.py",
            "tests/test_validate_low_token_workflow.py",
            "tests/test_validate_source_read_register.py",
            "tests/test_validate_planned_future_surfaces.py",
            "tests/test_validate_slice_packet.py",
            "plans/repo_roadmap.json",
            "plans/slices/slice_001_packet.json",
        ],
        "exact_owner_configs_schemas_contracts": [
            "schemas/methodology.schema.json",
            "schemas/slice_packet.schema.json",
            "schemas/refresh_decision.schema.json",
            "schemas/low_token_workflow_contract.schema.json",
            "schemas/repo_file_index.schema.json",
            "schemas/command_map.schema.json",
            "schemas/mature_repo_migration_packet.schema.json",
            "schemas/read_only_command_harness.schema.json",
            "schemas/source_read_register.schema.json",
            "schemas/planned_future_surfaces.schema.json",
            "contracts/command_map_contract.json",
            "contracts/low_token_workflow_contract.json",
            "contracts/read_only_command_harness.json",
            "plans/source_read_register.json",
            "plans/planned_future_surfaces.json",
        ],
        "required_source_reads": [
            {
                "read_id": "methodology_json",
                "surface": "copied local durable slice workflow methodology",
                "read_type": "docs",
                "status": "satisfied",
                "evidence_ref": "source_read:methodology_json",
            },
            {
                "read_id": "low_token_contract",
                "surface": "generic low-token workflow contract",
                "read_type": "docs",
                "status": "satisfied",
                "evidence_ref": "source_read:low_token_contract",
            },
            {
                "surface": "repo file inventory starter tools",
                "read_type": "docs",
                "status": "satisfied",
                "evidence_ref": "scripts/build_repo_file_index.py",
            },
            {
                "surface": "command map and mature-repo migration validators",
                "read_type": "docs",
                "status": "satisfied",
                "evidence_ref": "docs/MIGRATING_MATURE_REPO.md",
            },
            {
                "read_id": "read_only_harness_contract",
                "surface": "read-only command harness contract",
                "read_type": "docs",
                "status": "satisfied",
                "evidence_ref": "source_read:read_only_harness_contract",
            },
            {
                "surface": "beginner start and glossary documentation",
                "read_type": "docs",
                "status": "satisfied",
                "evidence_ref": "START_HERE.md",
            },
            {
                "read_id": "source_read_register_validator",
                "surface": "source-read register validator",
                "read_type": "full_source",
                "status": "satisfied",
                "evidence_ref": "source_read:source_read_register_validator",
            },
            {
                "read_id": "planned_future_surfaces_validator",
                "surface": "planned future surfaces validator",
                "read_type": "full_source",
                "status": "satisfied",
                "evidence_ref": "source_read:planned_future_surfaces_validator",
            }
        ],
        "owning_wave_validator": "scripts/validate_slice_packet.py",
        "owning_wave_tests": [
            "tests/test_validate_slice_packet.py",
            "tests/test_render_canonical_entrypoints.py",
        ],
        "focused_validators_and_tests": [
            "python scripts/render_canonical_entrypoints.py --check",
            "python scripts/validate_low_token_workflow.py --summary-only",
            "python scripts/build_repo_file_index.py --summary-only",
            "python scripts/build_command_map.py --summary-only",
            "python scripts/validate_command_map.py --summary-only",
            "python scripts/validate_read_only_commands.py --summary-only",
            (
                "python scripts/validate_slice_packet.py "
                "plans/slices/slice_001_packet.json --summary-only"
            ),
            "python -m pytest -q tests",
        ],
        "not_in_scope": [
            "Domain runtime implementation",
            "Generated index refresh",
            "Generated config variable inventory",
            "Generated helper command catalog",
            "Generated artifact output map",
            "External source access",
        ],
        "boundary_rules": {
            "allowed_scope": [
                "Copied durable slice workflow starter surfaces and starter packet proof"
            ],
            "forbidden_path_prefixes": [
                "manifests/",
                "receipts/"
            ],
            "forbidden_keywords": [
                "Domain runtime implementation",
                "External source access"
            ],
            "planned_future_surface_ids": [
                "config_variable_inventory",
                "helper_command_catalog",
                "artifact_output_map"
            ],
        },
        "refresh_decision": {
            "repo_index_required": False,
            "script_import_index_required": False,
            "plan_note_index_required": False,
            "config_variable_inventory_required": False,
            "output_schema_index_required": False,
            "post_output_hook_required": False,
            "next_wave_discovery_depends_on_new_surfaces": False,
            "required_reason": "focused starter validators and tests directly prove the bootstrap",
            "refresh_timing": "skip",
            "decision_basis": [
                "The first local bootstrap has no generated discovery surfaces.",
                "The next action is visible from the starter roadmap and packet.",
            ],
        },
        "commit_plan": {
            "implementation_commit": "local_durable_slice_workflow_bootstrap",
            "generated_refresh_commit": "not_required",
            "do_not_chase_head_only_staleness": True,
        },
    }


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def bootstrap(args: argparse.Namespace) -> int:
    target = args.target.resolve()
    project_name = args.project_name or target.name
    include_examples = args.include_examples or not args.no_examples
    planned = _planned_outputs(target, include_examples, not args.no_starter_plan)
    conflicts = [dst for dst, _src in planned if dst.exists()]

    if conflicts and not args.force:
        print(f"FAIL bootstrap_conflicts target={target} conflicts={len(conflicts)}")
        for path in conflicts[:25]:
            print(path.relative_to(target))
        if len(conflicts) > 25:
            print(f"... {len(conflicts) - 25} more")
        return 1

    if args.dry_run:
        print(f"DRY_RUN bootstrap target={target} files={len(planned)}")
        return 0

    target.mkdir(parents=True, exist_ok=True)
    for dst, src in planned:
        if src is None:
            continue
        _copy_file(src, dst, project_name)

    if not args.no_starter_plan:
        _write_json(target / "plans" / "repo_roadmap.json", _starter_roadmap(project_name))
        _write_json(
            target / "plans" / "slices" / "slice_001_packet.json",
            _starter_packet(),
        )

    print(f"PASS bootstrap target={target} files={len(planned)}")
    print("Next:")
    print("  cd", target)
    print("  read START_HERE.md")
    print("  python scripts/render_canonical_entrypoints.py --check")
    print("  python scripts/validate_low_token_workflow.py --summary-only")
    print("  python scripts/validate_source_read_register.py --summary-only")
    print("  python scripts/validate_planned_future_surfaces.py --summary-only")
    print("  python scripts/build_repo_file_index.py --summary-only")
    print("  python scripts/build_command_map.py --summary-only")
    print("  python scripts/validate_command_map.py --summary-only")
    print("  python scripts/validate_read_only_commands.py --summary-only")
    print(
        "  python scripts/validate_slice_packet.py "
        "plans/slices/slice_001_packet.json --summary-only"
    )
    print("  python -m pytest -q tests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--project-name")
    parser.add_argument("--include-examples", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--no-examples", action="store_true")
    parser.add_argument("--no-starter-plan", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return bootstrap(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
