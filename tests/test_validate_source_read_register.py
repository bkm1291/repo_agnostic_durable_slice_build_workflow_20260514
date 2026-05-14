from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_source_read_register.py"
REGISTER = ROOT / "plans" / "source_read_register.json"


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path), "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )


def base_register() -> dict:
    return {
        "schema_version": "v1.repo_agnostic_source_read_register.1",
        "register_id": "test_source_read_register",
        "status": "active",
        "purpose": "Track exact source reads for packet evidence.",
        "reads": [
            {
                "read_id": "methodology_json",
                "surface": "repo_agnostic_durable_slice_build_workflow_methodology_20260514.json",
                "surface_type": "repo_methodology",
                "read_type": "docs",
                "status": "satisfied",
                "owner_slice": "slice_001",
                "evidence_ref": "repo_agnostic_durable_slice_build_workflow_methodology_20260514.json",
                "summary": "Canonical methodology read for the starter workflow.",
            }
        ],
    }


def write_register(tmp_path: Path, register: dict) -> Path:
    path = tmp_path / "source_read_register.json"
    path.write_text(json.dumps(register, indent=2) + "\n", encoding="utf-8")
    return path


def test_default_source_read_register_validates() -> None:
    result = run_validator(REGISTER)

    assert result.returncode == 0
    assert "PASS source_read_register" in result.stdout


def test_duplicate_read_id_fails(tmp_path: Path) -> None:
    register = base_register()
    register["reads"].append(dict(register["reads"][0]))
    path = write_register(tmp_path, register)

    result = run_validator(path)

    assert result.returncode == 1
    assert "SOURCE_READ_ENTRY_DUPLICATE_ID" in result.stdout


def test_chat_only_evidence_fails(tmp_path: Path) -> None:
    register = base_register()
    register["reads"][0]["evidence_ref"] = "chat"
    path = write_register(tmp_path, register)

    result = run_validator(path)

    assert result.returncode == 1
    assert "SOURCE_READ_ENTRY_CHAT_ONLY_EVIDENCE" in result.stdout
