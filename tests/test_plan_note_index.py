from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_single_active_plan_resolution() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_plan_note_index.py"), "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["active_count"] >= 1


def test_query_active_only() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_plan_note_index.py"), "--write", "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "query_plan_note_index.py"), "--active-only", "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["match_count"] >= 1
