from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUERY = ROOT / "scripts" / "query_command_map.py"
BUILDER = ROOT / "scripts" / "build_command_map.py"


def run_command(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, text=True, capture_output=True)


def test_query_command_map_summary_is_read_only(tmp_path: Path) -> None:
    (tmp_path / "contracts").mkdir()
    (tmp_path / "contracts" / "read_only_command_harness.json").write_text(
        json.dumps({"commands": []}),
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.durable_slice_workflow.commands]
validate_demo = "python scripts/validate_demo.py --summary-only"
query_demo = "python scripts/query_demo.py --summary-only"
write_demo = "python scripts/write_demo.py --write --summary-only"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = run_command(
        [
            sys.executable,
            str(QUERY),
            "--root",
            str(tmp_path),
            "--safe-read-only",
            "--summary-only",
        ]
    )

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == "passed"
    assert payload["match_count"] == 0
    assert before == after


def test_query_live_command_map_by_command_id() -> None:
    result = run_command(
        [
            sys.executable,
            str(QUERY),
            "--command-id",
            "validate_command_map",
            "--summary-only",
        ]
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["match_count"] == 1
    assert payload["commands"][0]["command_id"] == "validate_command_map"
    assert payload["commands"][0]["entry_type"] == "validator"


def test_query_live_command_map_by_entry_type() -> None:
    result = run_command(
        [sys.executable, str(QUERY), "--entry-type", "validator", "--summary-only"]
    )

    payload = json.loads(result.stdout)
    command_ids = {entry["command_id"] for entry in payload["commands"]}
    assert result.returncode == 0
    assert payload["match_count"] >= 1
    assert "validate_command_map" in command_ids


def test_query_safe_read_only_excludes_writers() -> None:
    result = run_command(
        [sys.executable, str(QUERY), "--safe-read-only", "--summary-only"]
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["match_count"] >= 1
    assert all(
        entry["side_effect_class"] != "write_explicit" for entry in payload["commands"]
    )


def test_query_generated_command_map_file(tmp_path: Path) -> None:
    output = tmp_path / "command_map.json"
    write_result = run_command(
        [
            sys.executable,
            str(BUILDER),
            "--write",
            "--output",
            str(output),
            "--summary-only",
        ]
    )
    query_result = run_command(
        [
            sys.executable,
            str(QUERY),
            "--map",
            str(output),
            "--path-contains",
            "validate_command_map",
            "--summary-only",
        ]
    )

    payload = json.loads(query_result.stdout)
    assert write_result.returncode == 0
    assert query_result.returncode == 0
    assert payload["match_count"] >= 1
