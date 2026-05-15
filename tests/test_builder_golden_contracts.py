from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str) -> None:
    r = subprocess.run([sys.executable, *args], cwd=ROOT, check=False, text=True, capture_output=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_builder_outputs_have_stable_contract_headers() -> None:
    _run("scripts/build_repo_file_index.py", "--write", "--summary-only")
    _run("scripts/build_command_map.py", "--write", "--summary-only")
    _run("scripts/build_plan_note_index.py", "--write", "--summary-only")
    _run("scripts/build_artifact_output_map.py", "--write", "--summary-only")

    repo_idx = json.loads((ROOT / "manifests" / "repo_file_index.json").read_text(encoding="utf-8"))
    cmd_map = json.loads((ROOT / "manifests" / "command_map.json").read_text(encoding="utf-8"))
    note_idx = json.loads((ROOT / "manifests" / "plan_note_index.json").read_text(encoding="utf-8"))
    art_map = json.loads((ROOT / "manifests" / "artifact_output_map.json").read_text(encoding="utf-8"))

    assert repo_idx["schema_version"] == "v1.repo_file_index.1"
    assert cmd_map["schema_version"] == "v1.repo_agnostic_command_map.1"
    assert note_idx["schema_version"] == "v1.plan_note_index.1"
    assert art_map["schema_version"] == "v1.artifact_output_map.1"
