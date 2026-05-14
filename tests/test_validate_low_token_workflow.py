from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_low_token_workflow.py"
CONTRACT = ROOT / "contracts" / "low_token_workflow_contract.json"


def run_validator(path: Path = CONTRACT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path), "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
        cwd=ROOT,
    )


def write_contract(tmp_path: Path, contract: dict) -> Path:
    path = tmp_path / "low_token_workflow_contract.json"
    path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    return path


def load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def directory_snapshot(path: Path) -> dict[str, str]:
    return {
        str(item.relative_to(path)): item.read_text(encoding="utf-8")
        for item in sorted(path.rglob("*"))
        if item.is_file()
    }


def test_default_low_token_contract_passes() -> None:
    result = run_validator()

    assert result.returncode == 0
    assert "PASS low_token_workflow" in result.stdout


def test_targeted_read_limit_above_120_fails(tmp_path: Path) -> None:
    contract = load_contract()
    contract["default_limits"]["max_targeted_read_lines"] = 121
    path = write_contract(tmp_path, contract)

    result = run_validator(path)

    assert result.returncode == 1
    assert "LOW_TOKEN_TARGETED_READ_LIMIT_TOO_HIGH" in result.stdout


def test_raw_output_allowed_fails(tmp_path: Path) -> None:
    contract = load_contract()
    contract["default_limits"]["raw_sync_output_allowed"] = True
    path = write_contract(tmp_path, contract)

    result = run_validator(path)

    assert result.returncode == 1
    assert "LOW_TOKEN_RAW_SYNC_OUTPUT_NOT_DISABLED" in result.stdout


def test_escalation_phrase_requires_placeholders(tmp_path: Path) -> None:
    contract = load_contract()
    contract["read_escalation_ladder"]["required_escalation_phrase"] = "Need wider read."
    path = write_contract(tmp_path, contract)

    result = run_validator(path)

    assert result.returncode == 1
    assert "LOW_TOKEN_ESCALATION_PHRASE_MISSING_PLACEHOLDERS" in result.stdout


def test_summary_only_does_not_write_files(tmp_path: Path) -> None:
    contract = load_contract()
    path = write_contract(tmp_path, contract)
    before = directory_snapshot(tmp_path)

    result = run_validator(path)

    after = directory_snapshot(tmp_path)
    assert result.returncode == 0
    assert after == before
