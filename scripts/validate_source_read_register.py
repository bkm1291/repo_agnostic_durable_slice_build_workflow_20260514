#!/usr/bin/env python3
"""Validate the generic source-read/full-read register."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any
from _validator_output import emit_json


DEFAULT_REGISTER = Path("plans/source_read_register.json")
REQUIRED_TOP_FIELDS = ("schema_version", "register_id", "status", "purpose", "reads")
REQUIRED_READ_FIELDS = (
    "read_id",
    "surface",
    "surface_type",
    "read_type",
    "status",
    "owner_slice",
    "evidence_ref",
    "summary",
)
ALLOWED_READ_TYPES = {"full_source", "full_read", "attrs", "docs", "none"}
ALLOWED_STATUSES = {"satisfied", "deferred", "not_required"}
ALLOWED_SURFACE_TYPES = {
    "repo_methodology",
    "repo_doc",
    "contract",
    "schema",
    "validator",
    "runtime_source",
    "external_doc",
    "external_source",
    "other",
}
CHAT_ONLY_EVIDENCE = {"chat", "conversation", "memory"}


def _load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"SOURCE_READ_REGISTER_MISSING path={path}"]
    except json.JSONDecodeError as exc:
        return None, [f"SOURCE_READ_REGISTER_JSON_INVALID line={exc.lineno} column={exc.colno}"]


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_safe_repo_ref(value: str) -> bool:
    if "://" in value or value.startswith("source_read:"):
        return True
    if "/" not in value:
        return True
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def validate_register(document: Any) -> list[str]:
    if not isinstance(document, dict):
        return ["SOURCE_READ_REGISTER_NOT_OBJECT"]

    failures: list[str] = []
    for field in REQUIRED_TOP_FIELDS:
        if field not in document:
            failures.append(f"SOURCE_READ_REGISTER_MISSING_FIELD field={field}")

    if document.get("schema_version") != "v1.repo_agnostic_source_read_register.1":
        failures.append("SOURCE_READ_REGISTER_BAD_SCHEMA_VERSION")
    if document.get("status") not in {"active", "draft"}:
        failures.append("SOURCE_READ_REGISTER_BAD_STATUS")
    if not _is_nonempty_string(document.get("purpose")):
        failures.append("SOURCE_READ_REGISTER_PURPOSE_EMPTY")

    reads = document.get("reads")
    if not isinstance(reads, list) or not reads:
        failures.append("SOURCE_READ_REGISTER_READS_EMPTY")
        return failures

    seen: set[str] = set()
    for index, item in enumerate(reads):
        if not isinstance(item, dict):
            failures.append(f"SOURCE_READ_ENTRY_INVALID index={index}")
            continue
        for field in REQUIRED_READ_FIELDS:
            if field not in item:
                failures.append(f"SOURCE_READ_ENTRY_MISSING_FIELD index={index} field={field}")

        read_id = item.get("read_id")
        if not _is_nonempty_string(read_id):
            failures.append(f"SOURCE_READ_ENTRY_ID_EMPTY index={index}")
        elif str(read_id) in seen:
            failures.append(f"SOURCE_READ_ENTRY_DUPLICATE_ID read_id={read_id}")
        else:
            seen.add(str(read_id))

        for field in ("surface", "owner_slice", "evidence_ref", "summary"):
            if not _is_nonempty_string(item.get(field)):
                failures.append(f"SOURCE_READ_ENTRY_FIELD_EMPTY index={index} field={field}")

        if item.get("surface_type") not in ALLOWED_SURFACE_TYPES:
            failures.append(f"SOURCE_READ_ENTRY_BAD_SURFACE_TYPE index={index}")
        if item.get("read_type") not in ALLOWED_READ_TYPES:
            failures.append(f"SOURCE_READ_ENTRY_BAD_READ_TYPE index={index}")
        if item.get("status") not in ALLOWED_STATUSES:
            failures.append(f"SOURCE_READ_ENTRY_BAD_STATUS index={index}")
        if item.get("read_type") == "none" and item.get("status") != "not_required":
            failures.append(f"SOURCE_READ_ENTRY_NONE_STATUS_MISMATCH index={index}")

        evidence_ref = str(item.get("evidence_ref", "")).strip()
        if item.get("status") == "satisfied" and evidence_ref.lower() in CHAT_ONLY_EVIDENCE:
            failures.append(f"SOURCE_READ_ENTRY_CHAT_ONLY_EVIDENCE index={index}")
        if evidence_ref and not _is_safe_repo_ref(evidence_ref):
            failures.append(f"SOURCE_READ_ENTRY_UNSAFE_EVIDENCE_REF index={index}")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("register", nargs="?", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    document, load_failures = _load_json(args.register)
    failures = load_failures or validate_register(document)
    if failures:
        if args.json:
            emit_json(validator="source_read_register", status="failed", failure_codes=failures)
        else:
            print(f"FAIL source_read_register path={args.register} failures={len(failures)}")
            for failure in failures:
                print(failure)
        return 1

    if args.json:
        emit_json(validator="source_read_register", status="passed", failure_codes=[])
    elif args.summary_only:
        read_count = len(document.get("reads", [])) if isinstance(document, dict) else 0
        print(f"PASS source_read_register path={args.register} reads={read_count}")
    else:
        print(f"PASS source_read_register path={args.register} mode=check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
