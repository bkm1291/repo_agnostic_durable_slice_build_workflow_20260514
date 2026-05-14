#!/usr/bin/env python3
"""Validate and optionally run declared read-only commands under file snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any


DEFAULT_CONTRACT = Path("contracts/read_only_command_harness.json")
SHELL_METACHARS = (";", "&&", "||", "|", ">", "<", "`", "$(")
DEFAULT_IGNORE_DIRS = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__"}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_safe_relpath(value: str) -> bool:
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def _policy(contract: dict[str, Any]) -> dict[str, Any]:
    policy = contract.get("default_policy")
    return policy if isinstance(policy, dict) else {}


def _commands(contract: dict[str, Any]) -> list[dict[str, Any]]:
    commands = contract.get("commands")
    if not isinstance(commands, list):
        return []
    return [item for item in commands if isinstance(item, dict)]


def _validate_command(command: dict[str, Any], policy: dict[str, Any], failures: list[str]) -> None:
    command_id = command.get("command_id")
    if not isinstance(command_id, str) or not command_id.strip():
        failures.append("READ_ONLY_COMMAND_ID_EMPTY")
        command_id = "<unknown>"

    cwd = command.get("cwd", ".")
    if not isinstance(cwd, str) or not _is_safe_relpath(cwd):
        failures.append(f"READ_ONLY_COMMAND_BAD_CWD command_id={command_id}")

    argv = command.get("argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) and item for item in argv):
        failures.append(f"READ_ONLY_COMMAND_BAD_ARGV command_id={command_id}")
        return

    forbidden = set(str(item) for item in policy.get("forbidden_argv_tokens", []))
    for token in argv:
        if token in forbidden:
            failures.append(f"READ_ONLY_COMMAND_FORBIDDEN_TOKEN command_id={command_id} token={token}")
        if policy.get("forbid_shell_metacharacters") is True and any(meta in token for meta in SHELL_METACHARS):
            failures.append(f"READ_ONLY_COMMAND_SHELL_META command_id={command_id} token={token}")

    if command.get("compact_mode") is True:
        compact_tokens = [str(item) for item in policy.get("compact_mode_tokens", [])]
        if not any(token in argv for token in compact_tokens):
            failures.append(f"READ_ONLY_COMMAND_MISSING_COMPACT_MODE command_id={command_id}")

    expected = command.get("expected_exit_codes")
    if not isinstance(expected, list) or not expected or not all(isinstance(item, int) for item in expected):
        failures.append(f"READ_ONLY_COMMAND_BAD_EXPECTED_CODES command_id={command_id}")


def validate_contract(contract: Any) -> list[str]:
    if not isinstance(contract, dict):
        return ["READ_ONLY_CONTRACT_NOT_OBJECT"]
    failures: list[str] = []
    for field in ("schema_version", "contract_id", "status", "purpose", "default_policy", "commands"):
        if field not in contract:
            failures.append(f"READ_ONLY_CONTRACT_MISSING_FIELD field={field}")
    policy = _policy(contract)
    if policy.get("forbid_shell") is not True:
        failures.append("READ_ONLY_POLICY_SHELL_NOT_FORBIDDEN")
    if policy.get("forbid_shell_metacharacters") is not True:
        failures.append("READ_ONLY_POLICY_SHELL_META_NOT_FORBIDDEN")
    if not isinstance(policy.get("snapshot_roots"), list) or not policy.get("snapshot_roots"):
        failures.append("READ_ONLY_POLICY_SNAPSHOT_ROOTS_EMPTY")
    if not isinstance(policy.get("compact_mode_tokens"), list) or not policy.get("compact_mode_tokens"):
        failures.append("READ_ONLY_POLICY_COMPACT_TOKENS_EMPTY")

    seen: set[str] = set()
    commands = _commands(contract)
    if not commands:
        failures.append("READ_ONLY_COMMANDS_EMPTY")
    for command in commands:
        command_id = str(command.get("command_id", ""))
        if command_id in seen:
            failures.append(f"READ_ONLY_COMMAND_DUPLICATE_ID command_id={command_id}")
        seen.add(command_id)
        _validate_command(command, policy, failures)
    return failures


def _should_skip(path: Path, root: Path, ignore_dirs: set[str]) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in ignore_dirs for part in parts)


def _snapshot(root: Path, rel_roots: list[str], ignore_dirs: set[str]) -> dict[str, str]:
    state: dict[str, str] = {}
    for rel_root in rel_roots:
        base = root / rel_root
        if not base.exists():
            continue
        candidates = [base] if base.is_file() else sorted(base.rglob("*"))
        for item in candidates:
            if not item.is_file() or _should_skip(item, root, ignore_dirs):
                continue
            relpath = item.relative_to(root).as_posix()
            state[relpath] = hashlib.sha256(item.read_bytes()).hexdigest()
    return state


def _changed_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
    paths = sorted(set(before) | set(after))
    return [path for path in paths if before.get(path) != after.get(path)]


def _expand_argv(argv: list[str]) -> list[str]:
    return [sys.executable if token == "{python}" else token for token in argv]


def _run_command(root: Path, command: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    command_id = str(command["command_id"])
    cwd = root / str(command.get("cwd", "."))
    timeout = int(policy.get("timeout_seconds", 30))
    ignore_dirs = set(DEFAULT_IGNORE_DIRS)
    ignore_dirs.update(str(item) for item in policy.get("ignore_dirs", []))
    snapshot_roots = [str(item) for item in policy.get("snapshot_roots", ["."])]
    before = _snapshot(root, snapshot_roots, ignore_dirs)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        _expand_argv([str(item) for item in command["argv"]]),
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=env,
    )
    after = _snapshot(root, snapshot_roots, ignore_dirs)
    changed = _changed_paths(before, after)
    expected = set(int(item) for item in command.get("expected_exit_codes", [0]))
    failures: list[str] = []
    if result.returncode not in expected:
        failures.append("READ_ONLY_COMMAND_UNEXPECTED_EXIT")
    if changed:
        failures.append("READ_ONLY_COMMAND_MODIFIED_PATHS")
    return {
        "command_id": command_id,
        "returncode": result.returncode,
        "changed_path_count": len(changed),
        "changed_paths": changed[:25],
        "stdout_line_count": len(result.stdout.splitlines()),
        "stderr_line_count": len(result.stderr.splitlines()),
        "failures": failures,
    }


def run_commands(
    root: Path,
    contract: dict[str, Any],
    command_ids: list[str] | None,
) -> list[dict[str, Any]]:
    selected = _commands(contract)
    if command_ids:
        wanted = set(command_ids)
        selected = [command for command in selected if command.get("command_id") in wanted]
    policy = _policy(contract)
    return [_run_command(root, command, policy) for command in selected]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", nargs="?", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--command-id", action="append", default=[])
    parser.add_argument("--run", action="store_true", help="Execute selected commands under snapshots")
    parser.add_argument("--summary-only", action="store_true", help="Print compact JSON")
    args = parser.parse_args(argv)

    try:
        contract = _load_json(args.contract)
    except FileNotFoundError:
        print(json.dumps({"status": "failed", "failures": ["READ_ONLY_CONTRACT_MISSING"]}))
        return 1
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "failed", "failures": [f"READ_ONLY_CONTRACT_JSON_INVALID line={exc.lineno}"]}))
        return 1

    failures = validate_contract(contract)
    command_results: list[dict[str, Any]] = []
    if not failures and args.run:
        command_results = run_commands(args.root.resolve(), contract, args.command_id or None)
        for result in command_results:
            failures.extend(f"{failure} command_id={result['command_id']}" for failure in result["failures"])

    payload = {
        "status": "failed" if failures else "passed",
        "contract_path": args.contract.as_posix(),
        "checked_command_count": len(_commands(contract)) if isinstance(contract, dict) else 0,
        "executed_command_count": len(command_results),
        "failures": failures,
        "commands": command_results,
    }
    if args.summary_only:
        print(json.dumps(payload))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
