#!/usr/bin/env python3
"""Query the live or generated command/helper map with compact output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import build_command_map
import validate_command_map


def _load_document(args: argparse.Namespace) -> tuple[dict[str, Any] | None, str, list[str]]:
    if args.map:
        document, failures = validate_command_map._load_json(args.map)
        source = args.map.as_posix()
        if failures:
            return None, source, failures
        if not isinstance(document, dict):
            return None, source, ["COMMAND_MAP_NOT_OBJECT"]
        return document, source, validate_command_map.validate_command_map(document)

    source = "live"
    document = build_command_map.build_command_map(args.root.resolve())
    return document, source, validate_command_map.validate_command_map(document)


def _matches(entry: dict[str, Any], args: argparse.Namespace) -> bool:
    if args.command_id and entry.get("command_id") != args.command_id:
        return False
    if args.entry_type and entry.get("entry_type") != args.entry_type:
        return False
    if args.side_effect and entry.get("side_effect_class") != args.side_effect:
        return False
    if args.safe_read_only and entry.get("safe_to_run_in_read_only_harness") is not True:
        return False
    if args.path_contains and args.path_contains not in str(entry.get("path", "")):
        return False
    return True


def _compact_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "command_id": entry.get("command_id"),
        "entry_type": entry.get("entry_type"),
        "path": entry.get("path"),
        "argv_template": entry.get("argv_template"),
        "purpose": entry.get("purpose"),
        "side_effect_class": entry.get("side_effect_class"),
        "compact_mode_supported": entry.get("compact_mode_supported"),
        "safe_to_run_in_read_only_harness": entry.get("safe_to_run_in_read_only_harness"),
    }


def _query_payload(
    document: dict[str, Any],
    source: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    commands = document.get("commands", [])
    matches = [
        _compact_entry(entry)
        for entry in commands
        if isinstance(entry, dict) and _matches(entry, args)
    ]
    return {
        "status": "passed",
        "source": source,
        "match_count": len(matches),
        "filters": {
            "command_id": args.command_id,
            "entry_type": args.entry_type,
            "side_effect": args.side_effect,
            "safe_read_only": args.safe_read_only,
            "path_contains": args.path_contains,
        },
        "commands": matches,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--map", type=Path, help="Optional generated command map JSON")
    parser.add_argument("--command-id")
    parser.add_argument("--entry-type")
    parser.add_argument("--side-effect")
    parser.add_argument("--safe-read-only", action="store_true")
    parser.add_argument("--path-contains")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args(argv)

    document, source, failures = _load_document(args)
    if failures or document is None:
        payload = {
            "status": "failed",
            "source": source,
            "failure_count": len(failures),
            "failures": failures,
        }
        print(json.dumps(payload) if args.summary_only else json.dumps(payload, indent=2))
        return 1

    payload = _query_payload(document, source, args)
    print(json.dumps(payload) if args.summary_only else json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
