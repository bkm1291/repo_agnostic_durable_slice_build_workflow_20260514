#!/usr/bin/env python3
"""Minimal standalone slice-packet validator for the example repo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED = (
    "selected_wave_or_slice",
    "goal",
    "files_to_create_or_edit",
    "required_source_reads",
    "owning_wave_validator",
    "owning_wave_tests",
    "focused_validators_and_tests",
    "not_in_scope",
    "refresh_decision",
    "commit_plan",
)

REFRESH_FLAGS = (
    "repo_index_required",
    "script_import_index_required",
    "plan_note_index_required",
    "config_variable_inventory_required",
    "output_schema_index_required",
    "post_output_hook_required",
    "next_wave_discovery_depends_on_new_surfaces",
)


def validate(packet: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(packet, dict):
        return ["PACKET_NOT_OBJECT"]
    for field in REQUIRED:
        if field not in packet:
            failures.append(f"PACKET_MISSING_FIELD field={field}")
    refresh = packet.get("refresh_decision")
    if not isinstance(refresh, dict):
        failures.append("REFRESH_DECISION_NOT_OBJECT")
        return failures
    for field in REFRESH_FLAGS:
        if field not in refresh:
            failures.append(f"REFRESH_MISSING_FIELD field={field}")
        elif not isinstance(refresh[field], bool):
            failures.append(f"REFRESH_FLAG_NOT_BOOL field={field}")
    timing = refresh.get("refresh_timing")
    if all(isinstance(refresh.get(field), bool) for field in REFRESH_FLAGS):
        any_refresh = any(refresh[field] for field in REFRESH_FLAGS)
        if any_refresh and timing == "skip":
            failures.append("REFRESH_REQUIRED_WITH_SKIP_TIMING")
        if not any_refresh and timing != "skip":
            failures.append("REFRESH_NOT_REQUIRED_WITH_NON_SKIP_TIMING")
    reason = str(refresh.get("required_reason", "")).strip().lower()
    if reason in {"", "tbd", "maybe", "if needed", "as needed"}:
        failures.append("REFRESH_REASON_VAGUE")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL PACKET_JSON_INVALID line={exc.lineno}")
        return 1
    failures = validate(packet)
    if failures:
        print(f"FAIL slice_packet failures={len(failures)}")
        for failure in failures:
            print(failure)
        return 1
    print(f"PASS slice_packet path={args.packet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
