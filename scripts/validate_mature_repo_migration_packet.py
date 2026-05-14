#!/usr/bin/env python3
"""Validate a mature-repo migration packet before adopting this template."""

from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from pathlib import Path
from typing import Any


REQUIRED_TOP_FIELDS = (
    "schema_version",
    "migration_id",
    "status",
    "target_repo_path",
    "operator_goal",
    "adoption_mode",
    "existing_authority_surfaces",
    "protected_paths",
    "allowed_mutation_roots",
    "planned_template_surfaces",
    "required_preflight_commands",
    "validation_commands",
    "risk_register",
    "approval",
)
REQUIRED_AUTHORITY_FIELDS = (
    "path",
    "authority_class",
    "status",
    "migration_action",
    "evidence_ref",
)
REQUIRED_SURFACE_FIELDS = (
    "source_path",
    "target_path",
    "action",
    "overwrite_allowed",
    "reason",
)
ALLOWED_STATUSES = {"draft", "ready", "blocked", "adopted"}
ALLOWED_ADOPTION_MODES = {
    "reference_only",
    "copy_subset",
    "adapt_in_place",
    "full_template_migration",
}
ALLOWED_AUTHORITY_CLASSES = {
    "agent_rules",
    "skill",
    "readme",
    "roadmap",
    "ci",
    "release",
    "schema",
    "contract",
    "script",
    "other",
}
ALLOWED_AUTHORITY_ACTIONS = {"keep", "adapt", "supersede", "do_not_touch"}
ALLOWED_SURFACE_ACTIONS = {"copy", "adapt", "skip"}
VAGUE_VALUES = {"", "tbd", "todo", "maybe", "if needed", "as needed", "none", "n/a"}
HIGH_RISK_AUTHORITY_PATHS = {"AGENTS.md", "SKILL.md", "README.md", "pyproject.toml"}


def _load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"MIGRATION_PACKET_MISSING path={path}"]
    except json.JSONDecodeError as exc:
        return None, [f"MIGRATION_PACKET_JSON_INVALID line={exc.lineno} column={exc.colno}"]


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_vague(value: Any) -> bool:
    if not _is_nonempty_string(value):
        return True
    normalized = str(value).strip().lower()
    return normalized in VAGUE_VALUES or "tbd" in normalized or "todo" in normalized


def _is_safe_path(value: Any, *, allow_absolute: bool = False) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = PurePosixPath(value)
    if path.is_absolute() and not allow_absolute:
        return False
    return ".." not in path.parts and "\\" not in value


def _validate_string_list(
    value: Any,
    field: str,
    failures: list[str],
    *,
    min_items: int = 0,
    paths: bool = False,
    allow_absolute: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        failures.append(f"MIGRATION_FIELD_NOT_LIST field={field}")
        return []
    if len(value) < min_items:
        failures.append(f"MIGRATION_FIELD_LIST_TOO_SHORT field={field}")
    normalized_values: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if _is_vague(item):
            failures.append(f"MIGRATION_FIELD_LIST_ITEM_VAGUE field={field} index={index}")
            continue
        item_text = str(item).strip()
        if paths and not _is_safe_path(item_text, allow_absolute=allow_absolute):
            failures.append(f"MIGRATION_FIELD_LIST_ITEM_BAD_PATH field={field} index={index}")
            continue
        if item_text in seen:
            failures.append(f"MIGRATION_FIELD_LIST_DUPLICATE field={field} value={item_text}")
        seen.add(item_text)
        normalized_values.append(item_text)
    return normalized_values


def _path_is_under(path: str, roots: list[str]) -> bool:
    if not roots:
        return False
    normalized = path.strip("/")
    for root in roots:
        root_normalized = root.strip("/")
        if not root_normalized:
            continue
        if normalized == root_normalized or normalized.startswith(root_normalized + "/"):
            return True
    return False


def validate_packet(document: Any) -> list[str]:
    if not isinstance(document, dict):
        return ["MIGRATION_PACKET_NOT_OBJECT"]

    failures: list[str] = []
    for field in REQUIRED_TOP_FIELDS:
        if field not in document:
            failures.append(f"MIGRATION_PACKET_MISSING_FIELD field={field}")

    if document.get("schema_version") != "v1.repo_agnostic_mature_repo_migration_packet.1":
        failures.append("MIGRATION_PACKET_BAD_SCHEMA_VERSION")
    if document.get("status") not in ALLOWED_STATUSES:
        failures.append("MIGRATION_PACKET_BAD_STATUS")
    if _is_vague(document.get("migration_id")):
        failures.append("MIGRATION_ID_VAGUE")
    if _is_vague(document.get("operator_goal")):
        failures.append("MIGRATION_GOAL_VAGUE")
    if not _is_safe_path(document.get("target_repo_path"), allow_absolute=True):
        failures.append("MIGRATION_TARGET_REPO_PATH_BAD")

    adoption_mode = document.get("adoption_mode")
    if adoption_mode not in ALLOWED_ADOPTION_MODES:
        failures.append("MIGRATION_ADOPTION_MODE_BAD")

    protected_paths = _validate_string_list(
        document.get("protected_paths"),
        "protected_paths",
        failures,
        min_items=1,
        paths=True,
        allow_absolute=True,
    )
    allowed_roots = _validate_string_list(
        document.get("allowed_mutation_roots"),
        "allowed_mutation_roots",
        failures,
        paths=True,
        allow_absolute=True,
    )
    _validate_string_list(
        document.get("required_preflight_commands"),
        "required_preflight_commands",
        failures,
        min_items=1,
    )
    _validate_string_list(
        document.get("validation_commands"),
        "validation_commands",
        failures,
        min_items=1,
    )
    _validate_string_list(
        document.get("risk_register"),
        "risk_register",
        failures,
        min_items=1,
    )

    authority_surfaces = document.get("existing_authority_surfaces")
    authority_paths: set[str] = set()
    if not isinstance(authority_surfaces, list) or not authority_surfaces:
        failures.append("MIGRATION_AUTHORITY_SURFACES_EMPTY")
    else:
        for index, item in enumerate(authority_surfaces):
            if not isinstance(item, dict):
                failures.append(f"MIGRATION_AUTHORITY_SURFACE_INVALID index={index}")
                continue
            for field in REQUIRED_AUTHORITY_FIELDS:
                if field not in item:
                    failures.append(f"MIGRATION_AUTHORITY_SURFACE_MISSING_FIELD index={index} field={field}")
            path = item.get("path")
            if not _is_safe_path(path, allow_absolute=True):
                failures.append(f"MIGRATION_AUTHORITY_SURFACE_BAD_PATH index={index}")
            elif str(path) in authority_paths:
                failures.append(f"MIGRATION_AUTHORITY_SURFACE_DUPLICATE path={path}")
            else:
                authority_paths.add(str(path))
            if item.get("authority_class") not in ALLOWED_AUTHORITY_CLASSES:
                failures.append(f"MIGRATION_AUTHORITY_SURFACE_BAD_CLASS index={index}")
            if item.get("status") not in ALLOWED_AUTHORITY_ACTIONS:
                failures.append(f"MIGRATION_AUTHORITY_SURFACE_BAD_STATUS index={index}")
            if item.get("migration_action") not in ALLOWED_AUTHORITY_ACTIONS:
                failures.append(f"MIGRATION_AUTHORITY_SURFACE_BAD_ACTION index={index}")
            if _is_vague(item.get("evidence_ref")):
                failures.append(f"MIGRATION_AUTHORITY_SURFACE_EVIDENCE_VAGUE index={index}")

    missing_high_risk = sorted(HIGH_RISK_AUTHORITY_PATHS - authority_paths)
    if missing_high_risk:
        failures.append(f"MIGRATION_HIGH_RISK_AUTHORITY_UNCLASSIFIED paths={','.join(missing_high_risk)}")

    planned_surfaces = document.get("planned_template_surfaces")
    if not isinstance(planned_surfaces, list):
        failures.append("MIGRATION_TEMPLATE_SURFACES_NOT_LIST")
    else:
        for index, item in enumerate(planned_surfaces):
            if not isinstance(item, dict):
                failures.append(f"MIGRATION_TEMPLATE_SURFACE_INVALID index={index}")
                continue
            for field in REQUIRED_SURFACE_FIELDS:
                if field not in item:
                    failures.append(f"MIGRATION_TEMPLATE_SURFACE_MISSING_FIELD index={index} field={field}")
            source_path = item.get("source_path")
            target_path = item.get("target_path")
            if not _is_safe_path(source_path):
                failures.append(f"MIGRATION_TEMPLATE_SURFACE_BAD_SOURCE_PATH index={index}")
            if not _is_safe_path(target_path, allow_absolute=True):
                failures.append(f"MIGRATION_TEMPLATE_SURFACE_BAD_TARGET_PATH index={index}")
            if item.get("action") not in ALLOWED_SURFACE_ACTIONS:
                failures.append(f"MIGRATION_TEMPLATE_SURFACE_BAD_ACTION index={index}")
            if not isinstance(item.get("overwrite_allowed"), bool):
                failures.append(f"MIGRATION_TEMPLATE_SURFACE_OVERWRITE_NOT_BOOL index={index}")
            if _is_vague(item.get("reason")):
                failures.append(f"MIGRATION_TEMPLATE_SURFACE_REASON_VAGUE index={index}")
            if item.get("action") in {"copy", "adapt"} and not _path_is_under(str(target_path), allowed_roots):
                failures.append(f"MIGRATION_TEMPLATE_SURFACE_TARGET_OUTSIDE_ALLOWED_ROOT index={index}")
            if item.get("overwrite_allowed") is True and str(target_path) in protected_paths:
                failures.append(f"MIGRATION_TEMPLATE_SURFACE_OVERWRITES_PROTECTED_PATH index={index}")

    approval = document.get("approval")
    if not isinstance(approval, dict):
        failures.append("MIGRATION_APPROVAL_NOT_OBJECT")
    else:
        if approval.get("explicit_operator_approval_required") is not True:
            failures.append("MIGRATION_APPROVAL_REQUIRED_NOT_TRUE")
        if _is_vague(approval.get("approval_scope")):
            failures.append("MIGRATION_APPROVAL_SCOPE_VAGUE")
        approval_text = str(approval.get("approval_scope", "")).lower()
        if adoption_mode == "full_template_migration" and "full" not in approval_text:
            failures.append("MIGRATION_FULL_TEMPLATE_APPROVAL_SCOPE_MISSING")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args(argv)

    document, load_failures = _load_json(args.packet)
    failures = load_failures or validate_packet(document)
    if failures:
        print(f"FAIL mature_repo_migration_packet path={args.packet} failures={len(failures)}")
        for failure in failures:
            print(failure)
        return 1

    planned_count = (
        len(document.get("planned_template_surfaces", []))
        if isinstance(document, dict)
        else 0
    )
    if args.summary_only:
        print(f"PASS mature_repo_migration_packet path={args.packet} planned_surfaces={planned_count}")
    else:
        print(f"PASS mature_repo_migration_packet path={args.packet} mode=check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
