from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str, *args: str) -> int:
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], check=False).returncode


def test_cross_surface_warning_mode() -> None:
    assert run("validate_cross_surface_consistency.py", "--mode", "warning", "--summary-only") == 0


def test_future_note_materiality() -> None:
    assert run("validate_future_note_materiality.py", "--mode", "strict") == 0
