#!/usr/bin/env python3
"""Validate a durable slice packet using only the Python standard library."""

from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from pathlib import Path
from typing import Any


REQUIRED_PACKET_FIELDS = (
    "selected_wave_or_slice",
    "goal",
    "files_to_create_or_edit",
    "exact_owner_configs_schemas_contracts",
    "required_source_reads",
    "owning_wave_validator",
    "owning_wave_tests",
    "focused_validators_and_tests",
    "not_in_scope",
    "refresh_decision",
    "commit_plan",
)

REQUIRED_REFRESH_FIELDS = (
    "repo_index_required",
    "script_import_index_required",
    "plan_note_index_required",
    "config_variable_inventory_required",
    "output_schema_index_required",
    "post_output_hook_required",
    "next_wave_discovery_depends_on_new_surfaces",
    "required_reason",
    "refresh_timing",
    "decision_basis",
)

REFRESH_FLAGS = REQUIRED_REFRESH_FIELDS[:7]

ALLOWED_REFRESH_TIMINGS = {
    "skip",
    "after_implementation_commit",
    "after_plan_note_rebuild",
    "after_post_output_hook",
    "defer_to_release_closeout",
    "operator_requested",
}

VAGUE_REASONS = {
    "",
    "as needed",
    "if needed",
    "maybe",
    "n/a",
    "na",
    "none",
    "tbd",
    "todo",
}

NOT_REQUIRED_COMMIT_VALUES = {
    "not_required",
    "none",
    "skip",
    "only_if_refresh_decision_requires_it",
}


def _load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"PACKET_FILE_MISSING path={path}"]
    except json.JSONDecodeError as exc:
        return None, [f"PACKET_JSON_INVALID line={exc.lineno} column={exc.colno}"]


def _compact_packet(document: Any) -> Any:
    if isinstance(document, dict) and isinstance(document.get("compact_slice_packet"), dict):
        return document["compact_slice_packet"]
    return document


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_relative_repo_path(value: str) -> bool:
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def _validate_path_value(value: Any, field: str, failures: list[str]) -> None:
    if not _is_nonempty_string(value):
        failures.append(f"PACKET_FIELD_EMPTY field={field}")
        return
    if str(value).strip().lower() in {"none", "explicit none"}:
        return
    if not _is_relative_repo_path(value):
        failures.append(f"PACKET_PATH_NOT_REPO_RELATIVE field={field} path={value}")


def _command_mentions_path(command: str, path: str) -> bool:
    if path in command:
        return True
    parts = command.split()
    path_obj = PurePosixPath(path)
    for token in parts:
        token_path = PurePosixPath(token)
        if token == path:
            return True
        if token_path == path_obj:
            return True
        if token_path in path_obj.parents:
            return True
    return False


def _validate_no_duplicates(values: list[Any], field: str, failures: list[str]) -> None:
    seen: set[str] = set()
    for item in values:
        if not isinstance(item, str):
            continue
        normalized = item.strip()
        if normalized in seen:
            failures.append(f"PACKET_FIELD_DUPLICATE field={field} value={normalized}")
        seen.add(normalized)


def _validate_string_list(packet: dict[str, Any], field: str, failures: list[str]) -> None:
    value = packet.get(field)
    if not isinstance(value, list) or not value:
        failures.append(f"PACKET_FIELD_LIST_EMPTY field={field}")
        return
    _validate_no_duplicates(value, field, failures)
    for index, item in enumerate(value):
        if not _is_nonempty_string(item):
            failures.append(f"PACKET_FIELD_LIST_ITEM_INVALID field={field} index={index}")


def _validate_source_reads(value: Any, failures: list[str]) -> None:
    if not isinstance(value, list) or not value:
        failures.append("SOURCE_READS_EMPTY")
        return
    allowed_read_types = {"full_source", "attrs", "docs", "none"}
    allowed_statuses = {"satisfied", "deferred", "not_required"}
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            failures.append(f"SOURCE_READ_INVALID index={index}")
            continue
        for field in ("surface", "read_type", "status", "evidence_ref"):
            if field not in item:
                failures.append(f"SOURCE_READ_MISSING_FIELD index={index} field={field}")
        if item.get("read_type") not in allowed_read_types:
            failures.append(f"SOURCE_READ_BAD_TYPE index={index}")
        if item.get("status") not in allowed_statuses:
            failures.append(f"SOURCE_READ_BAD_STATUS index={index}")
        if item.get("read_type") == "none" and item.get("status") != "not_required":
            failures.append(f"SOURCE_READ_NONE_STATUS_MISMATCH index={index}")
        if item.get("read_type") != "none" and not _is_nonempty_string(item.get("evidence_ref")):
            failures.append(f"SOURCE_READ_EVIDENCE_EMPTY index={index}")


def _validate_refresh_decision(value: Any, failures: list[str]) -> None:
    if not isinstance(value, dict):
        failures.append("REFRESH_DECISION_NOT_OBJECT")
        return

    for field in REQUIRED_REFRESH_FIELDS:
        if field not in value:
            failures.append(f"REFRESH_MISSING_FIELD field={field}")

    for field in REFRESH_FLAGS:
        if field in value and not isinstance(value[field], bool):
            failures.append(f"REFRESH_FLAG_NOT_BOOL field={field}")

    reason = value.get("required_reason")
    normalized_reason = str(reason or "").strip().lower()
    if (
        not _is_nonempty_string(reason)
        or normalized_reason in VAGUE_REASONS
        or any(phrase in normalized_reason for phrase in ("if needed", "as needed", "tbd"))
    ):
        failures.append("REFRESH_REASON_VAGUE")

    timing = value.get("refresh_timing")
    if timing not in ALLOWED_REFRESH_TIMINGS:
        failures.append("REFRESH_TIMING_INVALID")

    basis = value.get("decision_basis")
    if not isinstance(basis, list) or not basis:
        failures.append("REFRESH_DECISION_BASIS_EMPTY")
    else:
        for index, item in enumerate(basis):
            if not _is_nonempty_string(item):
                failures.append(f"REFRESH_DECISION_BASIS_INVALID index={index}")

    if all(field in value and isinstance(value[field], bool) for field in REFRESH_FLAGS):
        any_refresh_required = any(value[field] for field in REFRESH_FLAGS)
        if any_refresh_required and timing == "skip":
            failures.append("REFRESH_REQUIRED_WITH_SKIP_TIMING")
        if not any_refresh_required and timing != "skip":
            failures.append("REFRESH_NOT_REQUIRED_WITH_NON_SKIP_TIMING")
        return


def _refresh_required(refresh_decision: Any) -> bool | None:
    if not isinstance(refresh_decision, dict):
        return None
    if not all(isinstance(refresh_decision.get(field), bool) for field in REFRESH_FLAGS):
        return None
    return any(refresh_decision[field] for field in REFRESH_FLAGS)


def _validate_commit_plan(value: Any, failures: list[str]) -> None:
    if not isinstance(value, dict):
        failures.append("COMMIT_PLAN_NOT_OBJECT")
        return
    for field in (
        "implementation_commit",
        "generated_refresh_commit",
        "do_not_chase_head_only_staleness",
    ):
        if field not in value:
            failures.append(f"COMMIT_PLAN_MISSING_FIELD field={field}")
    if "do_not_chase_head_only_staleness" in value and value[
        "do_not_chase_head_only_staleness"
    ] is not True:
        failures.append("COMMIT_PLAN_HEAD_CHASE_GUARD_NOT_TRUE")


def _validate_commit_refresh_consistency(
    packet: dict[str, Any], refresh_required: bool | None, failures: list[str]
) -> None:
    commit_plan = packet.get("commit_plan")
    if refresh_required is None or not isinstance(commit_plan, dict):
        return
    generated_commit = str(commit_plan.get("generated_refresh_commit", "")).strip().lower()
    if refresh_required and generated_commit in NOT_REQUIRED_COMMIT_VALUES:
        failures.append("COMMIT_PLAN_REFRESH_REQUIRED_BUT_GENERATED_COMMIT_NOT_REQUIRED")
    if not refresh_required and not generated_commit:
        failures.append("COMMIT_PLAN_GENERATED_REFRESH_COMMIT_EMPTY")


def _validate_focused_command_refs(packet: dict[str, Any], failures: list[str]) -> None:
    commands = packet.get("focused_validators_and_tests")
    if not isinstance(commands, list):
        return
    command_text = "\n".join(item for item in commands if isinstance(item, str))

    validator = packet.get("owning_wave_validator")
    if _is_nonempty_string(validator) and not _command_mentions_path(command_text, validator):
        failures.append("FOCUSED_COMMANDS_MISSING_OWNING_VALIDATOR")

    tests = packet.get("owning_wave_tests")
    if isinstance(tests, list):
        for test_path in tests:
            if _is_nonempty_string(test_path) and not _command_mentions_path(
                command_text, test_path
            ):
                failures.append(f"FOCUSED_COMMANDS_MISSING_OWNING_TEST path={test_path}")


def validate_packet(document: Any) -> list[str]:
    packet = _compact_packet(document)
    failures: list[str] = []

    if not isinstance(packet, dict):
        return ["PACKET_NOT_OBJECT"]

    for field in REQUIRED_PACKET_FIELDS:
        if field not in packet:
            failures.append(f"PACKET_MISSING_FIELD field={field}")

    for field in ("selected_wave_or_slice", "goal", "owning_wave_validator"):
        if field in packet and not _is_nonempty_string(packet[field]):
            failures.append(f"PACKET_FIELD_EMPTY field={field}")

    for field in (
        "files_to_create_or_edit",
        "owning_wave_tests",
        "focused_validators_and_tests",
        "not_in_scope",
    ):
        if field in packet:
            _validate_string_list(packet, field, failures)

    if "files_to_create_or_edit" in packet and isinstance(
        packet["files_to_create_or_edit"], list
    ):
        for path in packet["files_to_create_or_edit"]:
            _validate_path_value(path, "files_to_create_or_edit", failures)

    if "owning_wave_validator" in packet:
        _validate_path_value(packet["owning_wave_validator"], "owning_wave_validator", failures)

    if "owning_wave_tests" in packet and isinstance(packet["owning_wave_tests"], list):
        for path in packet["owning_wave_tests"]:
            _validate_path_value(path, "owning_wave_tests", failures)

    if "exact_owner_configs_schemas_contracts" in packet and not isinstance(
        packet["exact_owner_configs_schemas_contracts"], list
    ):
        failures.append("OWNER_CONFIGS_NOT_LIST")
    elif isinstance(packet.get("exact_owner_configs_schemas_contracts"), list):
        _validate_no_duplicates(
            packet["exact_owner_configs_schemas_contracts"],
            "exact_owner_configs_schemas_contracts",
            failures,
        )
        for path in packet["exact_owner_configs_schemas_contracts"]:
            _validate_path_value(path, "exact_owner_configs_schemas_contracts", failures)

    if "required_source_reads" in packet:
        _validate_source_reads(packet["required_source_reads"], failures)

    if "refresh_decision" in packet:
        _validate_refresh_decision(packet["refresh_decision"], failures)

    if "commit_plan" in packet:
        _validate_commit_plan(packet["commit_plan"], failures)

    _validate_commit_refresh_consistency(
        packet, _refresh_required(packet.get("refresh_decision")), failures
    )
    _validate_focused_command_refs(packet, failures)

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, help="Path to a slice packet JSON file")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print a compact result and do not write artifacts",
    )
    args = parser.parse_args(argv)

    document, load_failures = _load_json(args.packet)
    failures = load_failures or validate_packet(document)

    if failures:
        print(f"FAIL slice_packet path={args.packet} failures={len(failures)}")
        for failure in failures:
            print(failure)
        return 1

    if args.summary_only:
        print(f"PASS slice_packet path={args.packet}")
    else:
        print(f"PASS slice_packet path={args.packet} mode=check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
