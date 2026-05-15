from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_slice_closeout_json_mode_passes() -> None:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_slice_closeout.py"), "--mode", "strict", "--json"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["status"] == "passed"


def test_cross_surface_json_mode_passes() -> None:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_cross_surface_consistency.py"), "--mode", "strict", "--json"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["status"] == "passed"
