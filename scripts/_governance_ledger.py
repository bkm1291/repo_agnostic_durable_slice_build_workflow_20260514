from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


DEFAULT_LEDGER = Path("manifests/governance_event_ledger.jsonl")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "unknown"


def _short_head(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root,
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError:
        return "unknown"
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "unknown"


def _repo_ref(root: Path, path: Path | str) -> str:
    path_obj = Path(path)
    if not path_obj.is_absolute():
        value = path_obj.as_posix()
    else:
        try:
            value = path_obj.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            value = path_obj.name
    posix = PurePosixPath(value)
    if posix.is_absolute() or ".." in posix.parts or "\\" in value:
        return posix.name
    return value


def _existing_event_ids(ledger_path: Path) -> set[str]:
    if not ledger_path.exists():
        return set()
    ids: set[str] = set()
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and isinstance(event.get("event_id"), str):
            ids.add(event["event_id"])
    return ids


def append_generated_refresh_event(
    *,
    root: Path,
    writer_command_id: str,
    artifact_refs: list[Path | str],
    validator_ref: str,
    ledger_path: Path = DEFAULT_LEDGER,
    timestamp_utc: str | None = None,
) -> bool:
    return append_governance_event(
        root=root,
        event_type="generated_refresh",
        entity_id=writer_command_id,
        artifact_refs=artifact_refs,
        validator_ref=validator_ref,
        reason_class="generator",
        details={"writer_command_id": writer_command_id},
        ledger_path=ledger_path,
        timestamp_utc=timestamp_utc,
    )


def append_closeout_event(
    *,
    root: Path,
    closeout_id: str,
    artifact_refs: list[Path | str],
    validator_ref: str = "scripts/validate_slice_closeout.py",
    ledger_path: Path = DEFAULT_LEDGER,
    timestamp_utc: str | None = None,
    details: dict[str, Any] | None = None,
) -> bool:
    event_details = {"writer_command_id": "record_slice_closeout"}
    if details:
        event_details.update(details)
    return append_governance_event(
        root=root,
        event_type="closeout",
        entity_id=closeout_id,
        artifact_refs=artifact_refs,
        validator_ref=validator_ref,
        reason_class="closeout_gate",
        details=event_details,
        ledger_path=ledger_path,
        timestamp_utc=timestamp_utc,
    )


def append_release_gate_event(
    *,
    root: Path,
    artifact_refs: list[Path | str],
    validator_ref: str = "scripts/validate_release_package.py",
    ledger_path: Path = DEFAULT_LEDGER,
    timestamp_utc: str | None = None,
    details: dict[str, Any] | None = None,
) -> bool:
    event_details = {"writer_command_id": "record_release_gate"}
    if details:
        event_details.update(details)
    return append_governance_event(
        root=root,
        event_type="release_gate",
        entity_id="release_package",
        artifact_refs=artifact_refs,
        validator_ref=validator_ref,
        reason_class="closeout_gate",
        details=event_details,
        ledger_path=ledger_path,
        timestamp_utc=timestamp_utc,
    )


def append_governance_event(
    *,
    root: Path,
    event_type: str,
    entity_id: str,
    artifact_refs: list[Path | str],
    validator_ref: str,
    reason_class: str,
    details: dict[str, Any] | None = None,
    ledger_path: Path = DEFAULT_LEDGER,
    timestamp_utc: str | None = None,
) -> bool:
    root = root.resolve()
    ledger_abs = ledger_path if ledger_path.is_absolute() else root / ledger_path
    date_token = (timestamp_utc or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))[:10].replace("-", "")
    event_id = f"event_{_slug(event_type)}_{_slug(entity_id)}_{date_token}"
    if event_id in _existing_event_ids(ledger_abs):
        return False

    event_details: dict[str, Any] = {"reason_class": reason_class}
    if details:
        event_details.update(details)
    timestamp = timestamp_utc or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    event: dict[str, Any] = {
        "schema_version": "v1.governance_event.1",
        "event_id": event_id,
        "event_type": event_type,
        "entity_id": entity_id,
        "timestamp_utc": timestamp,
        "validator_ref": validator_ref,
        "artifact_refs": [_repo_ref(root, item) for item in artifact_refs],
        "commit_ref": _short_head(root),
        "details": event_details,
    }
    ledger_abs.parent.mkdir(parents=True, exist_ok=True)
    with ledger_abs.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
    return True
