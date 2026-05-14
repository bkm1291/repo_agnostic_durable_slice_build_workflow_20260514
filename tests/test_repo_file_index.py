from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_repo_file_index.py"
QUERY = ROOT / "scripts" / "query_repo_file_index.py"


def run_command(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, text=True, capture_output=True)


def test_build_repo_file_index_summary_is_read_only(tmp_path: Path) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "tool.py").write_text("print('ok')\n", encoding="utf-8")
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = run_command(
        [
            sys.executable,
            str(BUILDER),
            "--root",
            str(tmp_path),
            "--output",
            "manifests/repo_file_index.json",
            "--summary-only",
        ]
    )

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == "passed"
    assert payload["file_count"] == 1
    assert before == after


def test_build_repo_file_index_write_and_check(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    output = tmp_path / "manifests" / "repo_file_index.json"

    write_result = run_command(
        [
            sys.executable,
            str(BUILDER),
            "--root",
            str(tmp_path),
            "--output",
            "manifests/repo_file_index.json",
            "--write",
            "--summary-only",
        ]
    )
    check_result = run_command(
        [
            sys.executable,
            str(BUILDER),
            "--root",
            str(tmp_path),
            "--output",
            "manifests/repo_file_index.json",
            "--check",
            "--summary-only",
        ]
    )

    assert write_result.returncode == 0
    assert check_result.returncode == 0
    assert output.is_file()
    index = json.loads(output.read_text(encoding="utf-8"))
    assert index["files"][0]["path"] == "README.md"
    assert index["files"][0]["kind"] == "doc"


def test_query_repo_file_index_filters_by_kind(tmp_path: Path) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "tool.py").write_text("print('ok')\n", encoding="utf-8")
    index_path = tmp_path / "repo_file_index.json"
    build = run_command(
        [
            sys.executable,
            str(BUILDER),
            "--root",
            str(tmp_path),
            "--output",
            str(index_path),
            "--write",
            "--summary-only",
        ]
    )

    result = run_command(
        [
            sys.executable,
            str(QUERY),
            "--index",
            str(index_path),
            "--kind",
            "script",
            "--summary-only",
        ]
    )

    payload = json.loads(result.stdout)
    assert build.returncode == 0
    assert result.returncode == 0
    assert payload["match_count"] == 1
    assert payload["matches"][0]["path"] == "scripts/tool.py"


def test_query_missing_index_fails_compactly(tmp_path: Path) -> None:
    result = run_command(
        [
            sys.executable,
            str(QUERY),
            "--index",
            str(tmp_path / "missing.json"),
            "--summary-only",
        ]
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["failure"] == "REPO_FILE_INDEX_MISSING"
