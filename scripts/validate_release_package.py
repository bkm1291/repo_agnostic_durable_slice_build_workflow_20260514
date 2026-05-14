#!/usr/bin/env python3
"""Validate the public release package surface without external dependencies."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any


REQUIRED_PATHS = (
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "SKILL.md",
    "BUILD_STAGE_PROMPTS.md",
    "START_HERE.md",
    "PROMPT_FOR_NEW_AGENT.md",
    "RELEASE_CHECKLIST.md",
    "CHANGELOG.md",
    "LICENSE",
    ".gitignore",
    ".gitattributes",
    ".claude/skills/durable-slice/SKILL.md",
    ".claude/skills/durable-slice-audit/SKILL.md",
    ".claude/skills/durable-slice-release/SKILL.md",
    ".github/workflows/check.yml",
    "docs/CI.md",
    "docs/GLOSSARY.md",
    "docs/MIGRATING_MATURE_REPO.md",
    "docs/NEXT_ACTION_DECISION_TREE.md",
    "docs/TROUBLESHOOTING.md",
    "docs/ANNOTATED_SLICE_PACKET.md",
    "Makefile",
    "pyproject.toml",
    "repo_agnostic_durable_slice_build_workflow_methodology_20260514.json",
    "contracts/low_token_workflow_contract.json",
    "contracts/read_only_command_harness.json",
    "contracts/command_map_contract.json",
    "plans/source_read_register.json",
    "plans/planned_future_surfaces.json",
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
    "scripts/render_canonical_entrypoints.py",
    "scripts/bootstrap_local_repo.py",
    "scripts/validate_slice_packet.py",
    "scripts/validate_low_token_workflow.py",
    "scripts/build_repo_file_index.py",
    "scripts/query_repo_file_index.py",
    "scripts/build_command_map.py",
    "scripts/query_command_map.py",
    "scripts/validate_command_map.py",
    "scripts/validate_claude_integration.py",
    "scripts/validate_read_only_commands.py",
    "scripts/validate_source_read_register.py",
    "scripts/validate_planned_future_surfaces.py",
    "scripts/validate_mature_repo_migration_packet.py",
    "scripts/validate_release_package.py",
    "tests/test_validate_slice_packet.py",
    "tests/test_validate_low_token_workflow.py",
    "tests/test_repo_file_index.py",
    "tests/test_command_map.py",
    "tests/test_query_command_map.py",
    "tests/test_validate_claude_integration.py",
    "tests/test_validate_read_only_commands.py",
    "tests/test_validate_source_read_register.py",
    "tests/test_validate_planned_future_surfaces.py",
    "tests/test_validate_mature_repo_migration_packet.py",
    "tests/test_release_package.py",
    "tests/test_beginner_docs.py",
    "tests/test_bootstrap_local_repo.py",
    "tests/test_render_canonical_entrypoints.py",
    "examples/minimal_repo",
    "examples/small_config_tool_repo",
)

CI_REQUIRED_STRINGS = (
    "python-version",
    "3.11",
    "3.12",
    "make check",
    "make bootstrap-smoke",
    "make read-only-check",
    "actions/checkout@v5",
    "actions/setup-python@v6",
)

FORBIDDEN_PATH_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "tmp",
    "scratch",
}
FORBIDDEN_EXACT_PATHS = {
    "manifests/repo_file_index.json",
    "manifests/command_map.json",
}
FORBIDDEN_NAME_FRAGMENTS = (
    ".env",
    "secret",
    "credential",
    "private_key",
    "tokenized",
)

SUBPROCESS_CHECKS = (
    (
        "entrypoints_match_canonical",
        ["scripts/render_canonical_entrypoints.py", "--check"],
    ),
    (
        "minimal_example_packet_validates",
        [
            "scripts/validate_slice_packet.py",
            "examples/minimal_repo/plans/slices/slice_001_packet.json",
            "--summary-only",
        ],
    ),
    (
        "small_config_example_packet_validates",
        [
            "scripts/validate_slice_packet.py",
            "examples/small_config_tool_repo/plans/slices/slice_001_packet.json",
            "--summary-only",
        ],
    ),
    (
        "small_config_example_config_validates",
        [
            "examples/small_config_tool_repo/scripts/validate_greeting_config.py",
            "examples/small_config_tool_repo/configs/greeting_config.json",
            "--summary-only",
        ],
    ),
    (
        "claude_integration_validates",
        [
            "scripts/validate_claude_integration.py",
            "--summary-only",
        ],
    ),
)


def _safe_relpath(value: str) -> bool:
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def _load_pyproject(root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    path = root / "pyproject.toml"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, ["RELEASE_PYPROJECT_MISSING"]
    except tomllib.TOMLDecodeError as exc:
        return None, [f"RELEASE_PYPROJECT_INVALID line={exc.lineno} column={exc.colno}"]
    return data, []


def _tracked_or_packaged_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        return [line for line in result.stdout.splitlines() if line.strip()]

    paths: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        parts = set(PurePosixPath(relative).parts)
        if parts & {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
            continue
        paths.append(relative)
    return sorted(paths)


def _forbidden_release_path(path: str) -> str | None:
    if not _safe_relpath(path):
        return "RELEASE_TRACKED_PATH_UNSAFE"
    posix_path = PurePosixPath(path)
    parts = set(posix_path.parts)
    if parts & FORBIDDEN_PATH_PARTS:
        return "RELEASE_TRACKED_SCRATCH_OR_CACHE_PATH"
    if path in FORBIDDEN_EXACT_PATHS:
        return "RELEASE_TRACKED_GENERATED_MANIFEST"
    name = posix_path.name.lower()
    if name.startswith(".env") or any(fragment in name for fragment in FORBIDDEN_NAME_FRAGMENTS):
        return "RELEASE_TRACKED_PRIVATE_OR_SECRET_LIKE_PATH"
    return None


def _run_check(root: Path, check_id: str, argv: list[str]) -> list[str]:
    result = subprocess.run(
        [sys.executable, *argv],
        cwd=root,
        check=False,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if result.returncode == 0:
        return []
    return [f"RELEASE_SUBPROCESS_CHECK_FAILED check_id={check_id} returncode={result.returncode}"]


def _validate_required_paths(
    root: Path, required_paths: tuple[str, ...] | list[str]
) -> list[str]:
    failures: list[str] = []
    for relative in required_paths:
        if not _safe_relpath(relative):
            failures.append(f"RELEASE_REQUIRED_PATH_UNSAFE path={relative}")
            continue
        if not (root / relative).exists():
            failures.append(f"RELEASE_REQUIRED_PATH_MISSING path={relative}")
    return failures


def _validate_version(root: Path, pyproject: dict[str, Any] | None) -> list[str]:
    if not pyproject:
        return []
    project = pyproject.get("project")
    if not isinstance(project, dict):
        return ["RELEASE_PYPROJECT_PROJECT_TABLE_MISSING"]
    version = project.get("version")
    if not isinstance(version, str) or not version.strip():
        return ["RELEASE_PYPROJECT_VERSION_MISSING"]
    changelog = root / "CHANGELOG.md"
    try:
        changelog_text = changelog.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ["RELEASE_CHANGELOG_MISSING"]
    if f"## {version}" not in changelog_text and f"## v{version}" not in changelog_text:
        return [f"RELEASE_CHANGELOG_VERSION_MISMATCH version={version}"]
    return []


def _validate_ci(root: Path) -> list[str]:
    path = root / ".github" / "workflows" / "check.yml"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ["RELEASE_CI_WORKFLOW_MISSING"]
    failures = [
        f"RELEASE_CI_REQUIRED_TEXT_MISSING text={item}"
        for item in CI_REQUIRED_STRINGS
        if item not in text
    ]
    return failures


def validate_release_package(
    root: Path,
    *,
    run_subprocess_checks: bool = True,
    required_paths: tuple[str, ...] | list[str] = REQUIRED_PATHS,
    tracked_paths: list[str] | None = None,
) -> list[str]:
    root = root.resolve()
    failures: list[str] = []
    failures.extend(_validate_required_paths(root, required_paths))

    pyproject, pyproject_failures = _load_pyproject(root)
    failures.extend(pyproject_failures)
    failures.extend(_validate_version(root, pyproject))
    failures.extend(_validate_ci(root))

    paths = tracked_paths if tracked_paths is not None else _tracked_or_packaged_paths(root)
    for path in paths:
        reason = _forbidden_release_path(path)
        if reason:
            failures.append(f"{reason} path={path}")

    if run_subprocess_checks:
        for check_id, argv in SUBPROCESS_CHECKS:
            failures.extend(_run_check(root, check_id, argv))

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args(argv)

    failures = validate_release_package(args.root)
    if failures:
        if args.summary_only:
            payload = {
                "status": "failed",
                "failure_count": len(failures),
                "failures": failures,
            }
            print(json.dumps(payload))
        else:
            print(f"FAIL release_package root={args.root} failures={len(failures)}")
            for failure in failures:
                print(failure)
        return 1

    payload = {
        "status": "passed",
        "required_path_count": len(REQUIRED_PATHS),
        "subprocess_check_count": len(SUBPROCESS_CHECKS),
    }
    if args.summary_only:
        print(json.dumps(payload))
    else:
        print(
            "PASS release_package "
            f"root={args.root} "
            f"required_paths={payload['required_path_count']} "
            f"subprocess_checks={payload['subprocess_check_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
