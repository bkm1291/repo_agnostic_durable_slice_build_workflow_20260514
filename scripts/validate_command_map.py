#!/usr/bin/env python3
"""Validate the command/helper map and its semantic side-effect rules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any
from _validator_output import emit_json

import build_command_map


DEFAULT_MAP = Path("manifests/command_map.json")
REQUIRED_TOP_FIELDS = (
    "schema_version",
    "map_id",
    "status",
    "generated_by",
    "contract_ref",
    "authority_rule",
    "summary",
    "commands",
)
REQUIRED_AUTHORITY_FIELDS = (
    "schema_authority",
    "python_validator_authority",
    "conflict_rule",
)
REQUIRED_ENTRY_FIELDS = (
    "command_id",
    "entry_type",
    "path",
    "argv_template",
    "purpose",
    "side_effect_class",
    "compact_mode_supported",
    "writer_mode_requires_explicit_intent",
    "owner_area",
    "owner_refs",
    "validator_refs",
    "test_refs",
    "safe_to_run_in_read_only_harness",
)
ALLOWED_ENTRY_TYPES = {"command", "helper", "validator", "builder", "writer", "test"}
ALLOWED_SIDE_EFFECT_CLASSES = {
    "read_only",
    "read_only_summary",
    "write_explicit",
    "test_runner",
    "external_access",
    "unknown",
}
COMPACT_TOKENS = ("--summary-only", "--check", "-q")
WRITE_TOKENS = ("--write", "--record-ledger", "--force", "--delete", "--apply", "--in-place")


def _load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"COMMAND_MAP_MISSING path={path}"]
    except json.JSONDecodeError as exc:
        return None, [f"COMMAND_MAP_JSON_INVALID line={exc.lineno} column={exc.colno}"]


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_relative_repo_path(value: Any) -> bool:
    if value == "none":
        return True
    if not isinstance(value, str) or not value.strip():
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def _validate_string_list(value: Any, field: str, failures: list[str], *, min_items: int = 0) -> None:
    if not isinstance(value, list):
        failures.append(f"COMMAND_MAP_FIELD_NOT_LIST field={field}")
        return
    if len(value) < min_items:
        failures.append(f"COMMAND_MAP_FIELD_LIST_TOO_SHORT field={field}")
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not _is_nonempty_string(item):
            failures.append(f"COMMAND_MAP_FIELD_LIST_ITEM_EMPTY field={field} index={index}")
            continue
        normalized = str(item)
        if normalized in seen:
            failures.append(f"COMMAND_MAP_FIELD_LIST_DUPLICATE field={field} value={normalized}")
        seen.add(normalized)


def validate_command_map(document: Any) -> list[str]:
    if not isinstance(document, dict):
        return ["COMMAND_MAP_NOT_OBJECT"]

    failures: list[str] = []
    for field in REQUIRED_TOP_FIELDS:
        if field not in document:
            failures.append(f"COMMAND_MAP_MISSING_FIELD field={field}")

    if document.get("schema_version") != "v1.repo_agnostic_command_map.1":
        failures.append("COMMAND_MAP_BAD_SCHEMA_VERSION")
    if document.get("status") not in {"active", "draft"}:
        failures.append("COMMAND_MAP_BAD_STATUS")
    for field in ("generated_by", "contract_ref"):
        if not _is_relative_repo_path(document.get(field)):
            failures.append(f"COMMAND_MAP_BAD_PATH field={field}")

    authority = document.get("authority_rule")
    if not isinstance(authority, dict):
        failures.append("COMMAND_MAP_AUTHORITY_RULE_NOT_OBJECT")
    else:
        for field in REQUIRED_AUTHORITY_FIELDS:
            if not _is_nonempty_string(authority.get(field)):
                failures.append(f"COMMAND_MAP_AUTHORITY_RULE_MISSING field={field}")

    commands = document.get("commands")
    if not isinstance(commands, list) or not commands:
        failures.append("COMMAND_MAP_COMMANDS_EMPTY")
        return failures

    seen_ids: set[str] = set()
    entry_type_counts: dict[str, int] = {}
    side_effect_counts: dict[str, int] = {}

    for index, entry in enumerate(commands):
        if not isinstance(entry, dict):
            failures.append(f"COMMAND_MAP_ENTRY_INVALID index={index}")
            continue
        for field in REQUIRED_ENTRY_FIELDS:
            if field not in entry:
                failures.append(f"COMMAND_MAP_ENTRY_MISSING_FIELD index={index} field={field}")

        command_id = entry.get("command_id")
        if not _is_nonempty_string(command_id):
            failures.append(f"COMMAND_MAP_ENTRY_ID_EMPTY index={index}")
        elif str(command_id) in seen_ids:
            failures.append(f"COMMAND_MAP_ENTRY_DUPLICATE_ID command_id={command_id}")
        else:
            seen_ids.add(str(command_id))

        entry_type = entry.get("entry_type")
        if entry_type not in ALLOWED_ENTRY_TYPES:
            failures.append(f"COMMAND_MAP_ENTRY_BAD_TYPE command_id={command_id}")
        else:
            entry_type_counts[str(entry_type)] = entry_type_counts.get(str(entry_type), 0) + 1

        side_effect = entry.get("side_effect_class")
        if side_effect not in ALLOWED_SIDE_EFFECT_CLASSES:
            failures.append(f"COMMAND_MAP_ENTRY_BAD_SIDE_EFFECT command_id={command_id}")
        else:
            side_effect_counts[str(side_effect)] = side_effect_counts.get(str(side_effect), 0) + 1

        if not _is_relative_repo_path(entry.get("path")):
            failures.append(f"COMMAND_MAP_ENTRY_BAD_PATH command_id={command_id}")
        for field in ("argv_template", "purpose", "owner_area"):
            if not _is_nonempty_string(entry.get(field)):
                failures.append(f"COMMAND_MAP_ENTRY_FIELD_EMPTY command_id={command_id} field={field}")

        argv_template = str(entry.get("argv_template", ""))
        compact = entry.get("compact_mode_supported")
        if not isinstance(compact, bool):
            failures.append(f"COMMAND_MAP_ENTRY_COMPACT_NOT_BOOL command_id={command_id}")
        elif compact and not any(token in argv_template for token in COMPACT_TOKENS):
            failures.append(f"COMMAND_MAP_ENTRY_COMPACT_TOKEN_MISSING command_id={command_id}")

        writer_requires_intent = entry.get("writer_mode_requires_explicit_intent")
        if not isinstance(writer_requires_intent, bool):
            failures.append(f"COMMAND_MAP_ENTRY_WRITER_INTENT_NOT_BOOL command_id={command_id}")
        if side_effect == "write_explicit" and writer_requires_intent is not True:
            failures.append(f"COMMAND_MAP_WRITER_WITHOUT_EXPLICIT_INTENT command_id={command_id}")
        if any(token in argv_template for token in WRITE_TOKENS) and side_effect != "write_explicit":
            failures.append(f"COMMAND_MAP_WRITE_TOKEN_NOT_CLASSIFIED command_id={command_id}")

        safe_for_harness = entry.get("safe_to_run_in_read_only_harness")
        if not isinstance(safe_for_harness, bool):
            failures.append(f"COMMAND_MAP_ENTRY_SAFE_HARNESS_NOT_BOOL command_id={command_id}")
        if safe_for_harness and side_effect == "write_explicit":
            failures.append(f"COMMAND_MAP_HARNESS_WRITER_UNSAFE command_id={command_id}")
        if safe_for_harness and compact is not True:
            failures.append(f"COMMAND_MAP_HARNESS_COMMAND_NOT_COMPACT command_id={command_id}")

        _validate_string_list(entry.get("owner_refs"), "owner_refs", failures, min_items=1)
        _validate_string_list(entry.get("validator_refs"), "validator_refs", failures)
        _validate_string_list(entry.get("test_refs"), "test_refs", failures)

    summary = document.get("summary")
    if not isinstance(summary, dict):
        failures.append("COMMAND_MAP_SUMMARY_NOT_OBJECT")
    else:
        if summary.get("command_count") != len(commands):
            failures.append("COMMAND_MAP_SUMMARY_COMMAND_COUNT_MISMATCH")
        if summary.get("entry_type_counts") != dict(sorted(entry_type_counts.items())):
            failures.append("COMMAND_MAP_SUMMARY_ENTRY_TYPE_COUNT_MISMATCH")
        if summary.get("side_effect_counts") != dict(sorted(side_effect_counts.items())):
            failures.append("COMMAND_MAP_SUMMARY_SIDE_EFFECT_COUNT_MISMATCH")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command_map", nargs="?", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.command_map:
        document, load_failures = _load_json(args.command_map)
        source = args.command_map.as_posix()
    else:
        document = build_command_map.build_command_map(args.root.resolve())
        load_failures = []
        source = "live"

    failures = load_failures or validate_command_map(document)
    if failures:
        if args.json:
            emit_json(validator="command_map", status="failed", failure_codes=failures)
        else:
            print(f"FAIL command_map source={source} failures={len(failures)}")
            for failure in failures:
                print(failure)
        return 1

    command_count = len(document.get("commands", [])) if isinstance(document, dict) else 0
    if args.json:
        emit_json(validator="command_map", status="passed", failure_codes=[])
    elif args.summary_only:
        print(f"PASS command_map source={source} commands={command_count}")
    else:
        print(f"PASS command_map source={source} mode=check commands={command_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
