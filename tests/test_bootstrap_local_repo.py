from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap_local_repo.py"


def run_command(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, text=True, capture_output=True)


def test_bootstrap_creates_valid_local_repo(tmp_path: Path) -> None:
    target = tmp_path / "local-demo"
    result = run_command(
        [
            sys.executable,
            str(BOOTSTRAP),
            str(target),
            "--project-name",
            "Local Demo",
        ]
    )

    assert result.returncode == 0
    assert (target / "README.md").is_file()
    assert (target / "START_HERE.md").is_file()
    assert (target / "docs" / "GLOSSARY.md").is_file()
    assert (target / "docs" / "TROUBLESHOOTING.md").is_file()
    assert (target / "docs" / "NEXT_ACTION_DECISION_TREE.md").is_file()
    assert (target / "docs" / "ANNOTATED_SLICE_PACKET.md").is_file()
    assert (target / "LICENSE").is_file()
    assert (target / "CHANGELOG.md").is_file()
    assert (target / "Makefile").is_file()
    assert (target / "contracts" / "low_token_workflow_contract.json").is_file()
    assert (target / "contracts" / "read_only_command_harness.json").is_file()
    assert (target / "scripts" / "validate_low_token_workflow.py").is_file()
    assert (target / "scripts" / "build_repo_file_index.py").is_file()
    assert (target / "scripts" / "query_repo_file_index.py").is_file()
    assert (target / "scripts" / "validate_read_only_commands.py").is_file()
    assert (target / "plans" / "repo_roadmap.json").is_file()
    assert (target / "plans" / "slices" / "slice_001_packet.json").is_file()
    assert not (target / ".git").exists()
    assert 'name = "local-demo"' in (target / "pyproject.toml").read_text(
        encoding="utf-8"
    )

    render_check = run_command(
        [sys.executable, "scripts/render_canonical_entrypoints.py", "--check"],
        cwd=target,
    )
    packet_check = run_command(
        [
            sys.executable,
            "scripts/validate_slice_packet.py",
            "plans/slices/slice_001_packet.json",
            "--summary-only",
        ],
        cwd=target,
    )
    low_token_check = run_command(
        [sys.executable, "scripts/validate_low_token_workflow.py", "--summary-only"],
        cwd=target,
    )
    repo_index_summary = run_command(
        [sys.executable, "scripts/build_repo_file_index.py", "--summary-only"],
        cwd=target,
    )
    read_only_check = run_command(
        [sys.executable, "scripts/validate_read_only_commands.py", "--summary-only"],
        cwd=target,
    )

    assert render_check.returncode == 0
    assert packet_check.returncode == 0
    assert low_token_check.returncode == 0
    assert repo_index_summary.returncode == 0
    assert read_only_check.returncode == 0


def test_bootstrap_dry_run_does_not_create_target(tmp_path: Path) -> None:
    target = tmp_path / "dry-run-demo"
    result = run_command(
        [
            sys.executable,
            str(BOOTSTRAP),
            str(target),
            "--project-name",
            "Dry Run Demo",
            "--dry-run",
        ]
    )

    assert result.returncode == 0
    assert "DRY_RUN bootstrap" in result.stdout
    assert not target.exists()


def test_bootstrap_refuses_conflicts_without_force(tmp_path: Path) -> None:
    target = tmp_path / "conflict-demo"
    target.mkdir()
    (target / "README.md").write_text("existing\n", encoding="utf-8")

    result = run_command(
        [
            sys.executable,
            str(BOOTSTRAP),
            str(target),
            "--project-name",
            "Conflict Demo",
        ]
    )

    assert result.returncode == 1
    assert "FAIL bootstrap_conflicts" in result.stdout
    assert (target / "README.md").read_text(encoding="utf-8") == "existing\n"
