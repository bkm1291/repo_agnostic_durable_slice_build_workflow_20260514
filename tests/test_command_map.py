from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_command_map.py"
VALIDATOR = ROOT / "scripts" / "validate_command_map.py"


def run_command(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, text=True, capture_output=True)


def test_build_command_map_summary_is_read_only(tmp_path: Path) -> None:
    (tmp_path / "contracts").mkdir()
    (tmp_path / "contracts" / "read_only_command_harness.json").write_text(
        json.dumps({"commands": []}),
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.durable_slice_workflow.commands]
validate_demo = "python scripts/validate_demo.py --summary-only"
write_demo = "python scripts/write_demo.py --write --summary-only"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = run_command(
        [
            sys.executable,
            str(BUILDER),
            "--root",
            str(tmp_path),
            "--summary-only",
        ]
    )

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == "passed"
    assert payload["command_count"] == 2
    assert before == after


def test_build_command_map_write_then_validate(tmp_path: Path) -> None:
    (tmp_path / "contracts").mkdir()
    (tmp_path / "contracts" / "read_only_command_harness.json").write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command_id": "validate_demo",
                        "argv": ["python", "scripts/validate_demo.py", "--summary-only"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.durable_slice_workflow.commands]
validate_demo = "python scripts/validate_demo.py --summary-only"
write_demo = "python scripts/write_demo.py --write --summary-only"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "manifests" / "command_map.json"

    write_result = run_command(
        [
            sys.executable,
            str(BUILDER),
            "--root",
            str(tmp_path),
            "--write",
            "--summary-only",
        ]
    )
    validate_result = run_command(
        [sys.executable, str(VALIDATOR), str(output), "--summary-only"]
    )

    command_map = json.loads(output.read_text(encoding="utf-8"))
    by_id = {entry["command_id"]: entry for entry in command_map["commands"]}
    assert write_result.returncode == 0
    assert validate_result.returncode == 0
    assert by_id["validate_demo"]["safe_to_run_in_read_only_harness"] is True
    assert by_id["write_demo"]["side_effect_class"] == "write_explicit"
    assert by_id["write_demo"]["writer_mode_requires_explicit_intent"] is True


def test_validate_command_map_rejects_writer_without_explicit_intent(tmp_path: Path) -> None:
    command_map = {
        "schema_version": "v1.repo_agnostic_command_map.1",
        "map_id": "bad_map",
        "status": "active",
        "generated_by": "scripts/build_command_map.py",
        "contract_ref": "contracts/command_map_contract.json",
        "authority_rule": {
            "schema_authority": "schemas define document shape and enums",
            "python_validator_authority": "validators enforce semantic cross-file rules",
            "conflict_rule": "validator failure blocks closeout",
        },
        "summary": {
            "command_count": 1,
            "entry_type_counts": {"writer": 1},
            "side_effect_counts": {"write_explicit": 1},
        },
        "commands": [
            {
                "command_id": "write_demo",
                "entry_type": "writer",
                "path": "scripts/write_demo.py",
                "argv_template": "python scripts/write_demo.py --write --summary-only",
                "purpose": "Write demo output.",
                "side_effect_class": "write_explicit",
                "compact_mode_supported": True,
                "writer_mode_requires_explicit_intent": False,
                "owner_area": "workflow_scripts",
                "owner_refs": ["pyproject.toml"],
                "validator_refs": ["scripts/validate_command_map.py"],
                "test_refs": ["tests/test_command_map.py"],
                "safe_to_run_in_read_only_harness": False,
            }
        ],
    }
    path = tmp_path / "command_map.json"
    path.write_text(json.dumps(command_map, indent=2) + "\n", encoding="utf-8")

    result = run_command([sys.executable, str(VALIDATOR), str(path), "--summary-only"])

    assert result.returncode == 1
    assert "COMMAND_MAP_WRITER_WITHOUT_EXPLICIT_INTENT" in result.stdout


def test_validate_live_command_map_passes_for_template() -> None:
    result = run_command([sys.executable, str(VALIDATOR), "--summary-only"])

    assert result.returncode == 0
    assert "PASS command_map source=live" in result.stdout
