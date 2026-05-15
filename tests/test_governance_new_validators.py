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


def test_json_modes_emit_parseable_payloads() -> None:
    scripts = [
        "validate_plan_notes.py",
        "validate_slice_lifecycle.py",
        "validate_future_note_materiality.py",
    ]
    import json
    for name in scripts:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / name), "--mode", "strict", "--json"],
            check=False,
            text=True,
            capture_output=True,
        )
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["status"] in {"passed", "warn"}
