from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_summary_only_writer_not_marked() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_artifact_output_map.py"), "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_artifact_output_map.py"), "--write", "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )
    data = json.loads((ROOT / "manifests" / "artifact_output_map.json").read_text(encoding="utf-8"))
    assert all(not item["summary_only"] for item in data["outputs"])


def test_role_values_present() -> None:
    data = json.loads((ROOT / "manifests" / "artifact_output_map.json").read_text(encoding="utf-8"))
    assert {"authority", "evidence"} <= {item["role"] for item in data["outputs"]}
