#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath

from _validator_output import emit_json

DEFAULT_LEDGER = Path("manifests/governance_event_ledger.jsonl")
REQUIRED_FIELDS = (
    "schema_version",
    "event_id",
    "event_type",
    "entity_id",
    "timestamp_utc",
    "validator_ref",
    "artifact_refs",
    "commit_ref",
    "details",
)
REQUIRED_EVENT_TYPES = {"closeout", "generated_refresh", "release_gate", "external_action"}
ALLOWED_EVENT_TYPES = REQUIRED_EVENT_TYPES | {"materializer", "irreversible_decision"}
TS_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
ID_RE = re.compile(r"^event_[a-z0-9_]+_[0-9]{8}$")


def _safe_ref(value: str) -> bool:
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts and "\\" not in value


def validate_ledger(path: Path) -> list[str]:
    failures: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return [f"GOVERNANCE_LEDGER_MISSING path={path.as_posix()}"]

    if not lines:
        return ["GOVERNANCE_LEDGER_EMPTY"]

    seen_ids: set[str] = set()
    seen_types: set[str] = set()
    previous_timestamp = ""
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            failures.append(f"GOVERNANCE_LEDGER_BLANK_LINE line={index}")
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            failures.append(f"GOVERNANCE_LEDGER_JSON_INVALID line={index} column={exc.colno}")
            continue
        if not isinstance(event, dict):
            failures.append(f"GOVERNANCE_LEDGER_EVENT_NOT_OBJECT line={index}")
            continue
        for field in REQUIRED_FIELDS:
            if field not in event:
                failures.append(f"GOVERNANCE_LEDGER_MISSING_FIELD line={index} field={field}")
        if event.get("schema_version") != "v1.governance_event.1":
            failures.append(f"GOVERNANCE_LEDGER_BAD_SCHEMA line={index}")
        event_id = str(event.get("event_id", ""))
        if not ID_RE.match(event_id):
            failures.append(f"GOVERNANCE_LEDGER_BAD_EVENT_ID line={index}")
        if event_id in seen_ids:
            failures.append(f"GOVERNANCE_LEDGER_DUPLICATE_EVENT_ID event_id={event_id}")
        seen_ids.add(event_id)
        event_type = str(event.get("event_type", ""))
        if event_type not in ALLOWED_EVENT_TYPES:
            failures.append(f"GOVERNANCE_LEDGER_BAD_EVENT_TYPE line={index} event_type={event_type}")
        seen_types.add(event_type)
        timestamp = str(event.get("timestamp_utc", ""))
        if not TS_RE.match(timestamp):
            failures.append(f"GOVERNANCE_LEDGER_BAD_TIMESTAMP line={index}")
        if previous_timestamp and timestamp < previous_timestamp:
            failures.append(f"GOVERNANCE_LEDGER_TIMESTAMP_ORDER line={index}")
        previous_timestamp = timestamp
        validator_ref = str(event.get("validator_ref", ""))
        if not _safe_ref(validator_ref):
            failures.append(f"GOVERNANCE_LEDGER_BAD_VALIDATOR_REF line={index}")
        artifact_refs = event.get("artifact_refs")
        if not isinstance(artifact_refs, list) or not artifact_refs:
            failures.append(f"GOVERNANCE_LEDGER_ARTIFACT_REFS_EMPTY line={index}")
        else:
            for artifact_ref in artifact_refs:
                if not isinstance(artifact_ref, str) or not _safe_ref(artifact_ref):
                    failures.append(f"GOVERNANCE_LEDGER_BAD_ARTIFACT_REF line={index}")
        if not isinstance(event.get("details"), dict):
            failures.append(f"GOVERNANCE_LEDGER_DETAILS_NOT_OBJECT line={index}")

    missing_types = sorted(REQUIRED_EVENT_TYPES - seen_types)
    for event_type in missing_types:
        failures.append(f"GOVERNANCE_LEDGER_REQUIRED_EVENT_TYPE_MISSING event_type={event_type}")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", nargs="?", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    failures = validate_ledger(args.ledger)
    if failures:
        if args.json:
            emit_json(validator="governance_event_ledger", status="failed", failure_codes=failures)
        else:
            print(f"FAIL governance_event_ledger path={args.ledger} failures={len(failures)}")
            for failure in failures:
                print(failure)
        return 1
    if args.json:
        emit_json(validator="governance_event_ledger", status="passed", failure_codes=[])
    elif args.summary_only:
        line_count = len(args.ledger.read_text(encoding="utf-8").splitlines())
        print(f"PASS governance_event_ledger path={args.ledger} events={line_count}")
    else:
        print(f"PASS governance_event_ledger path={args.ledger} mode=check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
