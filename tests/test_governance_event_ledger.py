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
