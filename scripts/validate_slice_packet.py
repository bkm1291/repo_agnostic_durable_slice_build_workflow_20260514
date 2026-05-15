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
    "boundary_rules",
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

WRITE_INTENT_TOKENS = (
    " --write",
    " --force",
    " --delete",
    " --apply",
    " --in-place",
    " >",
    ">>",
    " rm ",
    " mv ",
)

REFRESH_FLAG_KEYWORDS = {
    "repo_index_required": ("repo index", "file inventory", "repo discovery", "repo map"),
    "script_import_index_required": ("script", "import", "command", "helper"),
    "plan_note_index_required": ("plan", "note", "roadmap"),
    "config_variable_inventory_required": ("config", "variable", "runtime field"),
    "output_schema_index_required": ("output", "schema", "artifact"),
    "post_output_hook_required": ("post output", "hook", "output hook"),
    "next_wave_discovery_depends_on_new_surfaces": (
        "next slice",
        "next wave",
        "future slice",
        "future wave",
        "future",
    ),
}

DEFAULT_SOURCE_READ_REGISTER = Path("plans/source_read_register.json")
DEFAULT_PLANNED_FUTURE_SURFACES = Path("plans/planned_future_surfaces.json")
ALLOWED_READ_TYPES = {"full_source", "full_read", "attrs", "docs", "none"}
ALLOWED_SOURCE_READ_STATUSES = {"satisfied", "deferred", "not_required"}
REQUIRED_BOUNDARY_FIELDS = (
    "allowed_scope",
    "forbidden_path_prefixes",
    "forbidden_keywords",
    "planned_future_surface_ids",
)


def _load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"PACKET_FILE_MISSING path={path}"]
    except json.JSONDecodeError as exc:
        return None, [f"PACKET_JSON_INVALID line={exc.lineno} column={exc.colno}"]


def _load_optional_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _compact_packet(document: Any) -> Any:
    if isinstance(document, dict) and isinstance(document.get("compact_slice_packet"), dict):
        return document["compact_slice_packet"]
    return document


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_vague_text(value: Any) -> bool:
    if not _is_nonempty_string(value):
        return True
    normalized = str(value).strip().lower()
    return normalized in VAGUE_REASONS or any(
        phrase in normalized for phrase in ("tbd", "todo", "if needed", "as needed")
    )


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
        elif _is_vague_text(item):
            failures.append(f"PACKET_FIELD_LIST_ITEM_VAGUE field={field} index={index}")


def _validate_not_in_scope_conflicts(packet: dict[str, Any], failures: list[str]) -> None:
    not_in_scope = packet.get("not_in_scope")
    edits = packet.get("files_to_create_or_edit")
    if not isinstance(not_in_scope, list) or not isinstance(edits, list):
        return
    lowered_edits = [str(x).lower() for x in edits if isinstance(x, str)]
    for item in not_in_scope:
        token = str(item).strip().lower()
        if not token:
            continue
        if any(token in e for e in lowered_edits):
            failures.append("NOT_IN_SCOPE_CONFLICTS_WITH_EDIT_LIST")
            return


def _source_read_register_by_id(source_read_register: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(source_read_register, dict):
        return {}
    reads = source_read_register.get("reads")
    if not isinstance(reads, list):
        return {}
    return {
        str(item["read_id"]): item
        for item in reads
        if isinstance(item, dict) and _is_nonempty_string(item.get("read_id"))
    }


def _planned_surfaces_by_id(planned_future_surfaces: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(planned_future_surfaces, dict):
        return {}
    surfaces = planned_future_surfaces.get("surfaces")
    if not isinstance(surfaces, list):
        return {}
    return {
        str(item["surface_id"]): item
        for item in surfaces
        if isinstance(item, dict) and _is_nonempty_string(item.get("surface_id"))
    }


def _evidence_source_read_ref(evidence_ref: Any) -> str | None:
    if not isinstance(evidence_ref, str):
        return None
    value = evidence_ref.strip()
    if value.startswith("source_read:"):
        return value.split(":", 1)[1].strip()
    return None


def _validate_source_reads(
    value: Any,
    failures: list[str],
    source_read_register: Any | None = None,
) -> None:
    if not isinstance(value, list) or not value:
        failures.append("SOURCE_READS_EMPTY")
        return
    register_by_id = _source_read_register_by_id(source_read_register)
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            failures.append(f"SOURCE_READ_INVALID index={index}")
            continue
        for field in ("surface", "read_type", "status", "evidence_ref"):
            if field not in item:
                failures.append(f"SOURCE_READ_MISSING_FIELD index={index} field={field}")
        if _is_vague_text(item.get("surface")):
            failures.append(f"SOURCE_READ_SURFACE_VAGUE index={index}")
        if item.get("read_type") not in ALLOWED_READ_TYPES:
            failures.append(f"SOURCE_READ_BAD_TYPE index={index}")
        if item.get("status") not in ALLOWED_SOURCE_READ_STATUSES:
            failures.append(f"SOURCE_READ_BAD_STATUS index={index}")
        if item.get("read_type") == "none" and item.get("status") != "not_required":
            failures.append(f"SOURCE_READ_NONE_STATUS_MISMATCH index={index}")
        if item.get("read_type") != "none" and not _is_nonempty_string(item.get("evidence_ref")):
            failures.append(f"SOURCE_READ_EVIDENCE_EMPTY index={index}")
        evidence_ref = str(item.get("evidence_ref", "")).strip()
        if item.get("status") == "satisfied" and evidence_ref.lower() in {"chat", "conversation", "memory"}:
            failures.append(f"SOURCE_READ_EVIDENCE_CHAT_ONLY index={index}")
        if evidence_ref and "/" in evidence_ref and not _is_relative_repo_path(evidence_ref):
            failures.append(f"SOURCE_READ_EVIDENCE_PATH_NOT_REPO_RELATIVE index={index}")

        read_id = item.get("read_id")
        evidence_read_id = _evidence_source_read_ref(item.get("evidence_ref"))
        if read_id is not None and not _is_nonempty_string(read_id):
            failures.append(f"SOURCE_READ_ID_EMPTY index={index}")
        if read_id and evidence_read_id and str(read_id) != evidence_read_id:
            failures.append(f"SOURCE_READ_ID_EVIDENCE_MISMATCH index={index}")

        referenced_id = str(read_id or evidence_read_id or "").strip()
        if referenced_id:
            if not register_by_id:
                failures.append(f"SOURCE_READ_REGISTER_UNAVAILABLE read_id={referenced_id}")
                continue
            register_entry = register_by_id.get(referenced_id)
            if register_entry is None:
                failures.append(f"SOURCE_READ_REGISTER_REF_NOT_FOUND read_id={referenced_id}")
                continue
            if item.get("read_type") != register_entry.get("read_type"):
                failures.append(f"SOURCE_READ_REGISTER_TYPE_MISMATCH read_id={referenced_id}")
            if item.get("status") == "satisfied" and register_entry.get("status") != "satisfied":
                failures.append(f"SOURCE_READ_REGISTER_STATUS_MISMATCH read_id={referenced_id}")
            if (
                evidence_ref
                and not evidence_ref.startswith("source_read:")
                and evidence_ref != register_entry.get("evidence_ref")
            ):
                failures.append(f"SOURCE_READ_REGISTER_EVIDENCE_MISMATCH read_id={referenced_id}")


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
            elif _is_vague_text(item):
                failures.append(f"REFRESH_DECISION_BASIS_VAGUE index={index}")

    if all(field in value and isinstance(value[field], bool) for field in REFRESH_FLAGS):
        any_refresh_required = any(value[field] for field in REFRESH_FLAGS)
        if any_refresh_required and timing == "skip":
            failures.append("REFRESH_REQUIRED_WITH_SKIP_TIMING")
        if not any_refresh_required and timing != "skip":
            failures.append("REFRESH_NOT_REQUIRED_WITH_NON_SKIP_TIMING")
        combined_basis = " ".join(str(item).lower() for item in basis or [])
        decision_text = f"{normalized_reason} {combined_basis}"
        for field, keywords in REFRESH_FLAG_KEYWORDS.items():
            if value.get(field) is True and not any(keyword in decision_text for keyword in keywords):
                failures.append(f"REFRESH_FLAG_REASON_MISSING_KEYWORD field={field}")
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
    for field in ("implementation_commit", "generated_refresh_commit"):
        if field in value and _is_vague_text(value[field]):
            failures.append(f"COMMIT_PLAN_FIELD_VAGUE field={field}")


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


def _validate_optional_string_list(value: Any, field: str, failures: list[str]) -> list[str]:
    if not isinstance(value, list):
        failures.append(f"BOUNDARY_FIELD_NOT_LIST field={field}")
        return []
    _validate_no_duplicates(value, f"boundary_rules.{field}", failures)
    normalized: list[str] = []
    for index, item in enumerate(value):
        if not _is_nonempty_string(item):
            failures.append(f"BOUNDARY_FIELD_ITEM_INVALID field={field} index={index}")
            continue
        if _is_vague_text(item):
            failures.append(f"BOUNDARY_FIELD_ITEM_VAGUE field={field} index={index}")
            continue
        normalized.append(str(item).strip())
    return normalized


def _not_in_scope_text(packet: dict[str, Any]) -> str:
    values = packet.get("not_in_scope")
    if not isinstance(values, list):
        return ""
    return " ".join(str(item).lower() for item in values if isinstance(item, str))


def _validate_boundary_rules(
    packet: dict[str, Any],
    planned_future_surfaces: Any | None,
    failures: list[str],
) -> None:
    value = packet.get("boundary_rules")
    if not isinstance(value, dict):
        failures.append("BOUNDARY_RULES_NOT_OBJECT")
        return

    for field in REQUIRED_BOUNDARY_FIELDS:
        if field not in value:
            failures.append(f"BOUNDARY_RULES_MISSING_FIELD field={field}")

    allowed_scope = _validate_optional_string_list(
        value.get("allowed_scope"), "allowed_scope", failures
    )
    if not allowed_scope:
        failures.append("BOUNDARY_ALLOWED_SCOPE_EMPTY")

    forbidden_prefixes = _validate_optional_string_list(
        value.get("forbidden_path_prefixes"), "forbidden_path_prefixes", failures
    )
    forbidden_keywords = _validate_optional_string_list(
        value.get("forbidden_keywords"), "forbidden_keywords", failures
    )
    planned_surface_ids = _validate_optional_string_list(
        value.get("planned_future_surface_ids"), "planned_future_surface_ids", failures
    )

    edited_paths = [
        str(item)
        for item in packet.get("files_to_create_or_edit", [])
        if isinstance(item, str)
    ]
    for prefix in forbidden_prefixes:
        if not _is_relative_repo_path(prefix):
            failures.append(f"BOUNDARY_FORBIDDEN_PREFIX_NOT_REPO_RELATIVE prefix={prefix}")
            continue
        for path in edited_paths:
            if path == prefix or path.startswith(prefix.rstrip("/") + "/"):
                failures.append(f"BOUNDARY_FORBIDDEN_PATH_PREFIX_MATCH prefix={prefix} path={path}")

    not_in_scope_text = _not_in_scope_text(packet)
    scope_text = " ".join(
        str(packet.get(field, "")).lower() for field in ("goal", "selected_wave_or_slice")
    )
    scope_text = f"{scope_text} {' '.join(path.lower() for path in edited_paths)}"
    for keyword in forbidden_keywords:
        normalized = keyword.lower()
        if normalized not in not_in_scope_text:
            failures.append(f"BOUNDARY_KEYWORD_NOT_IN_SCOPE keyword={keyword}")
        if normalized in scope_text:
            failures.append(f"BOUNDARY_FORBIDDEN_KEYWORD_IN_SCOPE keyword={keyword}")

    if not planned_surface_ids:
        return

    surfaces_by_id = _planned_surfaces_by_id(planned_future_surfaces)
    if not surfaces_by_id:
        failures.append("BOUNDARY_PLANNED_SURFACES_REGISTER_UNAVAILABLE")
        return

    selected = str(packet.get("selected_wave_or_slice", ""))
    for surface_id in planned_surface_ids:
        surface = surfaces_by_id.get(surface_id)
        if surface is None:
            failures.append(f"BOUNDARY_PLANNED_SURFACE_REF_NOT_FOUND surface_id={surface_id}")
            continue
        surface_path = str(surface.get("path", ""))
        surface_owner = str(surface.get("owner_slice", ""))
        surface_status = str(surface.get("status", ""))
        planned_tokens = [
            surface_id.lower(),
            surface_id.replace("_", " ").lower(),
            surface_path.lower(),
        ]
        if not any(token and token in not_in_scope_text for token in planned_tokens):
            failures.append(f"BOUNDARY_PLANNED_SURFACE_NOT_IN_SCOPE surface_id={surface_id}")
        if surface_path in edited_paths and surface_owner != selected:
            failures.append(
                f"BOUNDARY_PLANNED_SURFACE_WRONG_OWNER surface_id={surface_id} owner={surface_owner}"
            )
        if surface_path in edited_paths and surface_status == "planned_not_created":
            failures.append(f"BOUNDARY_PLANNED_SURFACE_STILL_PLANNED surface_id={surface_id}")


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


def _validate_focused_commands_are_read_only(packet: dict[str, Any], failures: list[str]) -> None:
    commands = packet.get("focused_validators_and_tests")
    if not isinstance(commands, list):
        return
    for index, command in enumerate(commands):
        if not isinstance(command, str):
            continue
        padded = f" {command.strip().lower()} "
        if any(token in padded for token in WRITE_INTENT_TOKENS):
            failures.append(f"FOCUSED_COMMANDS_CONTAIN_WRITE_INTENT index={index}")


def validate_packet(
    document: Any,
    source_read_register: Any | None = None,
    planned_future_surfaces: Any | None = None,
) -> list[str]:
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
        elif field in packet and field != "owning_wave_validator" and _is_vague_text(packet[field]):
            failures.append(f"PACKET_FIELD_VAGUE field={field}")

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
        _validate_source_reads(packet["required_source_reads"], failures, source_read_register)

    if "boundary_rules" in packet:
        _validate_boundary_rules(packet, planned_future_surfaces, failures)

    if "refresh_decision" in packet:
        _validate_refresh_decision(packet["refresh_decision"], failures)

    if "commit_plan" in packet:
        _validate_commit_plan(packet["commit_plan"], failures)

    _validate_commit_refresh_consistency(
        packet, _refresh_required(packet.get("refresh_decision")), failures
    )
    _validate_not_in_scope_conflicts(packet, failures)
    _validate_focused_command_refs(packet, failures)
    _validate_focused_commands_are_read_only(packet, failures)

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, help="Path to a slice packet JSON file")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print a compact result and do not write artifacts",
    )
    parser.add_argument(
        "--source-read-register",
        type=Path,
        default=DEFAULT_SOURCE_READ_REGISTER,
        help="Optional source-read register used to resolve source_read:<id> evidence refs",
    )
    parser.add_argument(
        "--planned-future-surfaces",
        type=Path,
        default=DEFAULT_PLANNED_FUTURE_SURFACES,
        help="Optional planned-future-surfaces registry used by boundary_rules",
    )
    args = parser.parse_args(argv)

    document, load_failures = _load_json(args.packet)
    source_read_register = _load_optional_json(args.source_read_register)
    planned_future_surfaces = _load_optional_json(args.planned_future_surfaces)
    failures = load_failures or validate_packet(
        document,
        source_read_register=source_read_register,
        planned_future_surfaces=planned_future_surfaces,
    )

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
