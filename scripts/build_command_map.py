#!/usr/bin/env python3
"""Build or check a compact command/helper map using only the standard library."""

from __future__ import annotations

import argparse
import json
import tomllib
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

from _governance_ledger import append_generated_refresh_event


DEFAULT_OUTPUT = Path("manifests/command_map.json")
DEFAULT_CONTRACT = Path("contracts/command_map_contract.json")
DEFAULT_READ_ONLY_CONTRACT = Path("contracts/read_only_command_harness.json")
DEFAULT_PYPROJECT = Path("pyproject.toml")

AUTHORITY_RULE = {
    "schema_authority": (
        "schemas define JSON shape, required fields, allowed enum values, "
        "and portable structural constraints"
    ),
    "python_validator_authority": (
        "Python validators define semantic rules, cross-file rules, "
        "side-effect rules, read-only checks, and local adoption safety"
    ),
    "conflict_rule": (
        "When a schema accepts a document but the Python validator rejects it, "
        "the validator rejection blocks closeout until the schema or document is intentionally updated."
    ),
}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _safe_relpath(value: str) -> bool:
    if value == "none":
        return True
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def _load_pyproject_commands(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    commands = (
        data.get("tool", {})
        .get("durable_slice_workflow", {})
        .get("commands", {})
    )
    if not isinstance(commands, dict):
        return {}
    return {
        str(command_id): str(template)
        for command_id, template in commands.items()
        if isinstance(command_id, str) and isinstance(template, str)
    }


def _read_only_command_ids(contract: dict[str, Any]) -> set[str]:
    commands = contract.get("commands")
    if not isinstance(commands, list):
        return set()
    return {
        str(item.get("command_id"))
        for item in commands
        if isinstance(item, dict) and isinstance(item.get("command_id"), str)
    }


def _path_from_template(template: str) -> str:
    tokens = template.split()
    for token in tokens:
        cleaned = token.strip("'\"")
        if cleaned.endswith(".py") and _safe_relpath(cleaned):
            return cleaned
    if tokens and tokens[0] == "make":
        return "Makefile"
    return "none"


def _entry_type(command_id: str, path: str, template: str) -> str:
    if command_id.startswith("validate_") or Path(path).name.startswith("validate_"):
        return "validator"
    if command_id.startswith("build_") or Path(path).name.startswith("build_"):
        return "builder"
    if command_id.startswith("write_") or " --write" in f" {template} ":
        return "writer"
    if "pytest" in template or command_id.endswith("_test") or command_id.endswith("_tests"):
        return "test"
    if command_id.startswith("query_") or Path(path).name.startswith("query_"):
        return "helper"
    return "command"


def _side_effect_class(command_id: str, template: str, entry_type: str) -> str:
    padded = f" {template} "
    if " --write" in padded or command_id.startswith("write_"):
        return "write_explicit"
    if "bootstrap" in command_id or "bootstrap_local_repo.py" in template:
        return "write_explicit"
    if entry_type == "test" or "pytest" in template or command_id.startswith("make_"):
        return "test_runner"
    if "--summary-only" in template:
        return "read_only_summary"
    if "--check" in template or entry_type in {"validator", "helper"}:
        return "read_only"
    return "unknown"


def _owner_area(path: str, entry_type: str) -> str:
    if path == "none":
        return entry_type
    parts = PurePosixPath(path).parts
    if not parts:
        return entry_type
    if parts[0] == "scripts":
        return "workflow_scripts"
    if parts[0] == "tests":
        return "tests"
    return parts[0]


def _purpose(command_id: str, entry_type: str, template: str) -> str:
    if entry_type == "validator":
        return f"Validate {command_id.replace('_', ' ')} with compact output where available."
    if entry_type == "builder":
        return f"Build or summarize {command_id.replace('_', ' ')} discovery evidence."
    if entry_type == "writer":
        return f"Write {command_id.replace('_', ' ')} only when explicit writer mode is requested."
    if entry_type == "helper":
        return f"Query or route {command_id.replace('_', ' ')} without broad manual discovery."
    if entry_type == "test":
        return f"Run focused or repo tests through {template}."
    return f"Run {command_id.replace('_', ' ')}."


def _entry(
    command_id: str,
    template: str,
    read_only_ids: set[str],
) -> dict[str, Any]:
    path = _path_from_template(template)
    entry_type = _entry_type(command_id, path, template)
    side_effect_class = _side_effect_class(command_id, template, entry_type)
    return {
        "command_id": command_id,
        "entry_type": entry_type,
        "path": path,
        "argv_template": template,
        "purpose": _purpose(command_id, entry_type, template),
        "side_effect_class": side_effect_class,
        "compact_mode_supported": any(
            token in template for token in ("--summary-only", "--check", "-q")
        ),
        "writer_mode_requires_explicit_intent": side_effect_class == "write_explicit",
        "owner_area": _owner_area(path, entry_type),
        "owner_refs": [
            "pyproject.toml",
            "contracts/command_map_contract.json",
        ],
        "validator_refs": [
            "scripts/validate_command_map.py",
        ],
        "test_refs": [
            "tests/test_command_map.py",
        ],
        "safe_to_run_in_read_only_harness": command_id in read_only_ids,
    }


def build_command_map(
    root: Path,
    contract_path: Path = DEFAULT_CONTRACT,
    read_only_contract_path: Path = DEFAULT_READ_ONLY_CONTRACT,
) -> dict[str, Any]:
    root = root.resolve()
    commands = _load_pyproject_commands(root / DEFAULT_PYPROJECT)
    read_only_ids = _read_only_command_ids(_load_json(root / read_only_contract_path))
    entries = [
        _entry(command_id, template, read_only_ids)
        for command_id, template in sorted(commands.items())
    ]
    entry_type_counts = Counter(entry["entry_type"] for entry in entries)
    side_effect_counts = Counter(entry["side_effect_class"] for entry in entries)
    return {
        "schema_version": "v1.repo_agnostic_command_map.1",
        "map_id": "repo_agnostic_command_map",
        "status": "active",
        "generated_by": "scripts/build_command_map.py",
        "contract_ref": contract_path.as_posix(),
        "authority_rule": AUTHORITY_RULE,
        "summary": {
            "command_count": len(entries),
            "entry_type_counts": dict(sorted(entry_type_counts.items())),
            "side_effect_counts": dict(sorted(side_effect_counts.items())),
        },
        "commands": entries,
    }


def _stable_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _summary_payload(command_map: dict[str, Any], *, status: str, output_path: Path) -> dict[str, Any]:
    return {
        "status": status,
        "map_id": command_map.get("map_id"),
        "command_count": command_map.get("summary", {}).get("command_count"),
        "entry_type_counts": command_map.get("summary", {}).get("entry_type_counts", {}),
        "side_effect_counts": command_map.get("summary", {}).get("side_effect_counts", {}),
        "output_path": output_path.as_posix(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Write the generated command map")
    mode.add_argument("--check", action="store_true", help="Fail if the output map is missing or stale")
    parser.add_argument("--summary-only", action="store_true", help="Print compact JSON")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    output_abs = args.output if args.output.is_absolute() else root / args.output
    command_map = build_command_map(root)
    expected = _stable_json(command_map)

    if args.write:
        output_abs.parent.mkdir(parents=True, exist_ok=True)
        output_abs.write_text(expected, encoding="utf-8")
        ledger_appended = append_generated_refresh_event(
            root=root,
            writer_command_id="write_command_map",
            artifact_refs=[output_abs],
            validator_ref="scripts/build_command_map.py",
        )
        summary = _summary_payload(command_map, status="passed", output_path=args.output)
        summary["ledger_appended"] = ledger_appended
        print(json.dumps(summary))
        return 0

    if args.check:
        if not output_abs.exists():
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "failure": "COMMAND_MAP_MISSING",
                        "output_path": args.output.as_posix(),
                    }
                )
            )
            return 1
        current = output_abs.read_text(encoding="utf-8")
        if current != expected:
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "failure": "COMMAND_MAP_STALE",
                        "output_path": args.output.as_posix(),
                    }
                )
            )
            return 1
        print(json.dumps(_summary_payload(command_map, status="passed", output_path=args.output)))
        return 0

    print(json.dumps(_summary_payload(command_map, status="passed", output_path=args.output)))
    if not args.summary_only:
        print(_stable_json(command_map), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
