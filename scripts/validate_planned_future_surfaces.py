#!/usr/bin/env python3
"""Validate the generic planned-future-surfaces registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any


DEFAULT_REGISTRY = Path("plans/planned_future_surfaces.json")
REQUIRED_TOP_FIELDS = ("schema_version", "registry_id", "status", "purpose", "surfaces")
REQUIRED_SURFACE_FIELDS = (
    "surface_id",
    "path",
    "surface_type",
    "status",
    "owner_slice",
    "activation_packet",
    "reason",
)
ALLOWED_SURFACE_TYPES = {
    "config",
    "schema",
    "contract",
    "script",
    "test",
    "doc",
    "plan",
    "generated_index",
    "artifact",
    "other",
}
ALLOWED_STATUSES = {"planned_not_created", "active", "blocked", "superseded"}


def _load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"PLANNED_SURFACES_MISSING path={path}"]
    except json.JSONDecodeError as exc:
        return None, [f"PLANNED_SURFACES_JSON_INVALID line={exc.lineno} column={exc.colno}"]


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_relative_repo_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def validate_registry(document: Any) -> list[str]:
    if not isinstance(document, dict):
        return ["PLANNED_SURFACES_NOT_OBJECT"]

    failures: list[str] = []
    for field in REQUIRED_TOP_FIELDS:
        if field not in document:
            failures.append(f"PLANNED_SURFACES_MISSING_FIELD field={field}")

    if document.get("schema_version") != "v1.repo_agnostic_planned_future_surfaces.1":
        failures.append("PLANNED_SURFACES_BAD_SCHEMA_VERSION")
    if document.get("status") not in {"active", "draft"}:
        failures.append("PLANNED_SURFACES_BAD_STATUS")
    if not _is_nonempty_string(document.get("purpose")):
        failures.append("PLANNED_SURFACES_PURPOSE_EMPTY")

    surfaces = document.get("surfaces")
    if not isinstance(surfaces, list):
        failures.append("PLANNED_SURFACES_LIST_INVALID")
        return failures

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, item in enumerate(surfaces):
        if not isinstance(item, dict):
            failures.append(f"PLANNED_SURFACE_INVALID index={index}")
            continue
        for field in REQUIRED_SURFACE_FIELDS:
            if field not in item:
                failures.append(f"PLANNED_SURFACE_MISSING_FIELD index={index} field={field}")

        surface_id = item.get("surface_id")
        if not _is_nonempty_string(surface_id):
            failures.append(f"PLANNED_SURFACE_ID_EMPTY index={index}")
        elif str(surface_id) in seen_ids:
            failures.append(f"PLANNED_SURFACE_DUPLICATE_ID surface_id={surface_id}")
        else:
            seen_ids.add(str(surface_id))

        path = item.get("path")
        if not _is_relative_repo_path(path):
            failures.append(f"PLANNED_SURFACE_BAD_PATH index={index}")
        elif str(path) in seen_paths:
            failures.append(f"PLANNED_SURFACE_DUPLICATE_PATH path={path}")
        else:
            seen_paths.add(str(path))

        if item.get("surface_type") not in ALLOWED_SURFACE_TYPES:
            failures.append(f"PLANNED_SURFACE_BAD_TYPE index={index}")
        if item.get("status") not in ALLOWED_STATUSES:
            failures.append(f"PLANNED_SURFACE_BAD_STATUS index={index}")
        if not _is_nonempty_string(item.get("owner_slice")):
            failures.append(f"PLANNED_SURFACE_OWNER_EMPTY index={index}")
        if not _is_relative_repo_path(item.get("activation_packet")):
            failures.append(f"PLANNED_SURFACE_BAD_ACTIVATION_PACKET index={index}")
        if not _is_nonempty_string(item.get("reason")):
            failures.append(f"PLANNED_SURFACE_REASON_EMPTY index={index}")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", nargs="?", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args(argv)

    document, load_failures = _load_json(args.registry)
    failures = load_failures or validate_registry(document)
    if failures:
        print(f"FAIL planned_future_surfaces path={args.registry} failures={len(failures)}")
        for failure in failures:
            print(failure)
        return 1

    if args.summary_only:
        count = len(document.get("surfaces", [])) if isinstance(document, dict) else 0
        print(f"PASS planned_future_surfaces path={args.registry} surfaces={count}")
    else:
        print(f"PASS planned_future_surfaces path={args.registry} mode=check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
