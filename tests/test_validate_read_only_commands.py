from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_read_only_commands.py"
CONTRACT = ROOT / "contracts" / "read_only_command_harness.json"


def run_validator(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
    )


def base_contract() -> dict:
    return {
        "schema_version": "v1.repo_agnostic_read_only_command_harness.1",
        "contract_id": "test_read_only_contract",
        "status": "active",
        "purpose": "Test read-only command behavior.",
        "default_policy": {
            "forbid_shell": True,
            "forbid_shell_metacharacters": True,
            "compact_mode_tokens": ["--summary-only", "--check", "-q"],
            "forbidden_argv_tokens": ["--write", "--force"],
            "snapshot_roots": ["."],
            "compare_git_porcelain_before_after": True,
            "stdout_stderr_secret_scan": True,
            "secret_scan_patterns": [
                {
                    "name": "secret_assignment",
                    "pattern": (
                        r"(?i)\b(password|passwd|api[_-]?key|secret|token)\s*[:=]\s*"
                        r"['\"]?[A-Za-z0-9._~+/=-]{8,}"
                    ),
                }
            ],
            "ignore_dirs": [".git", "__pycache__"],
            "timeout_seconds": 10,
        },
        "commands": [],
    }


def write_contract(tmp_path: Path, contract: dict) -> Path:
    path = tmp_path / "read_only_command_harness.json"
    path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    return path


def test_default_read_only_contract_validates() -> None:
    result = run_validator([str(CONTRACT), "--summary-only"])

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == "passed"


def test_run_read_only_command_does_not_change_snapshot(tmp_path: Path) -> None:
    contract = base_contract()
    contract["commands"].append(
        {
            "command_id": "print_only",
            "cwd": ".",
            "argv": ["{python}", "-c", "print('ok')", "--summary-only"],
            "expected_exit_codes": [0],
            "compact_mode": True,
        }
    )
    path = write_contract(tmp_path, contract)

    result = run_validator([str(path), "--root", str(tmp_path), "--run", "--summary-only"])

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == "passed"
    assert payload["commands"][0]["changed_path_count"] == 0


def test_run_writer_command_fails_on_snapshot_change(tmp_path: Path) -> None:
    contract = base_contract()
    contract["commands"].append(
        {
            "command_id": "writes_file",
            "cwd": ".",
            "argv": [
                "{python}",
                "-c",
                "open('created.txt', 'w', encoding='utf-8').write('x')",
                "--summary-only",
            ],
            "expected_exit_codes": [0],
            "compact_mode": True,
        }
    )
    path = write_contract(tmp_path, contract)

    result = run_validator([str(path), "--root", str(tmp_path), "--run", "--summary-only"])

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "READ_ONLY_COMMAND_MODIFIED_PATHS command_id=writes_file" in payload["failures"]


def test_forbidden_write_flag_fails_contract(tmp_path: Path) -> None:
    contract = base_contract()
    contract["commands"].append(
        {
            "command_id": "write_flag",
            "cwd": ".",
            "argv": ["{python}", "script.py", "--write", "--summary-only"],
            "expected_exit_codes": [0],
            "compact_mode": True,
        }
    )
    path = write_contract(tmp_path, contract)

    result = run_validator([str(path), "--summary-only"])

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "READ_ONLY_COMMAND_FORBIDDEN_TOKEN command_id=write_flag token=--write" in payload["failures"]


def test_secret_like_output_fails_run(tmp_path: Path) -> None:
    contract = base_contract()
    contract["commands"].append(
        {
            "command_id": "prints_secret",
            "cwd": ".",
            "argv": [
                "{python}",
                "-c",
                "print('token=abc123456789')",
                "--summary-only",
            ],
            "expected_exit_codes": [0],
            "compact_mode": True,
        }
    )
    path = write_contract(tmp_path, contract)

    result = run_validator([str(path), "--root", str(tmp_path), "--run", "--summary-only"])

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "READ_ONLY_COMMAND_SECRET_OUTPUT command_id=prints_secret" in payload["failures"]
