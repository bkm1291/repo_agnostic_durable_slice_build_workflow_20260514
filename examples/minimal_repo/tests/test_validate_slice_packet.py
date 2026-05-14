from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_slice_packet.py"
PACKET = ROOT / "plans" / "slices" / "slice_001_packet.json"


def test_example_packet_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(PACKET), "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "PASS slice_packet" in result.stdout


def test_vague_refresh_reason_fails(tmp_path: Path) -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    packet["refresh_decision"]["required_reason"] = "maybe"
    bad_packet = tmp_path / "bad_packet.json"
    bad_packet.write_text(json.dumps(packet), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(bad_packet), "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "REFRESH_REASON_VAGUE" in result.stdout
