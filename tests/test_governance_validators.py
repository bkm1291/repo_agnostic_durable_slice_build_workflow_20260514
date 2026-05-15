from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(script: str) -> int:
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--summary-only"], check=False).returncode


def test_runtime_dirs_validator_passes() -> None:
    assert _run("validate_runtime_governance_dirs.py") == 0


def test_receipts_checkpoints_validator_passes() -> None:
    assert _run("validate_receipts_checkpoints.py") == 0
