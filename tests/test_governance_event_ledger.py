from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_governance_event_ledger_validates_json_mode() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_governance_event_ledger.py"), "--json"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["validator"] == "governance_event_ledger"
    assert payload["status"] == "passed"


def test_writer_appends_ledger_event_idempotently(tmp_path: Path) -> None:
    root = tmp_path / "fixture_repo"
    root.mkdir()
    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_artifact_output_map.py"),
                "--root",
                str(root),
                "--write",
                "--summary-only",
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0

    ledger = root / "manifests" / "governance_event_ledger.jsonl"
    lines = ledger.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["event_type"] == "generated_refresh"
    assert event["details"]["writer_command_id"] == "write_artifact_output_map"


def test_closeout_command_records_ledger_event_idempotently(tmp_path: Path) -> None:
    root = tmp_path / "fixture_repo"
    closeouts = root / "closeouts"
    closeouts.mkdir(parents=True)
    closeout = closeouts / "slice_demo_closeout.json"
    closeout.write_text(
        json.dumps(
            {
                "implementation_commit": "abc1234",
                "generated_refresh_required": False,
                "proof_commands": ["python -m pytest -q tests/test_demo.py"],
                "residual_classification": "none",
                "next_slice_ready": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    ledger = root / "manifests" / "governance_event_ledger.jsonl"

    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_slice_closeout.py"),
                str(closeout),
                "--root",
                str(root),
                "--mode",
                "strict",
                "--record-ledger",
                "--ledger-path",
                str(ledger),
                "--timestamp-utc",
                "2026-05-15T00:00:00Z",
                "--summary-only",
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0

    lines = ledger.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["event_id"] == "event_closeout_slice_demo_20260515"
    assert event["event_type"] == "closeout"
    assert event["entity_id"] == "slice_demo"
    assert event["details"]["writer_command_id"] == "record_slice_closeout"


def test_release_command_records_ledger_event_idempotently(tmp_path: Path) -> None:
    ledger = tmp_path / "governance_event_ledger.jsonl"

    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_release_package.py"),
                "--record-ledger",
                "--ledger-path",
                str(ledger),
                "--timestamp-utc",
                "2026-05-15T00:00:00Z",
                "--summary-only",
            ],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0

    lines = ledger.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["event_id"] == "event_release_gate_release_package_20260515"
    assert event["event_type"] == "release_gate"
    assert event["entity_id"] == "release_package"
    assert event["details"]["writer_command_id"] == "record_release_gate"
