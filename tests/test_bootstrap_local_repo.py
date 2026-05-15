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
    assert (target / "CLAUDE.md").is_file()
    assert (target / "START_HERE.md").is_file()
    assert (target / "PROMPT_FOR_NEW_AGENT.md").is_file()
    assert (target / "PROJECT_GOAL.template.md").is_file()
    assert not (target / "PROJECT_GOAL.md").exists()
    assert (target / "RELEASE_CHECKLIST.md").is_file()
    assert (target / ".github" / "workflows" / "check.yml").is_file()
    assert (target / ".claude" / "skills" / "durable-slice" / "SKILL.md").is_file()
    assert (target / ".claude" / "skills" / "durable-slice-audit" / "SKILL.md").is_file()
    assert (target / ".claude" / "skills" / "durable-slice-release" / "SKILL.md").is_file()
    assert (target / "docs" / "CI.md").is_file()
    assert (target / "docs" / "GLOSSARY.md").is_file()
    assert (target / "docs" / "MIGRATING_MATURE_REPO.md").is_file()
    assert (target / "docs" / "TROUBLESHOOTING.md").is_file()
    assert (target / "docs" / "NEXT_ACTION_DECISION_TREE.md").is_file()
    assert (target / "docs" / "ANNOTATED_SLICE_PACKET.md").is_file()
    assert (target / "LICENSE").is_file()
    assert (target / "CHANGELOG.md").is_file()
    assert (target / "Makefile").is_file()
    assert (target / "contracts" / "low_token_workflow_contract.json").is_file()
    assert (target / "contracts" / "command_map_contract.json").is_file()
    assert (target / "contracts" / "read_only_command_harness.json").is_file()
    assert (target / "plans" / "source_read_register.json").is_file()
    assert (target / "plans" / "planned_future_surfaces.json").is_file()
    assert (target / "manifests" / "governance_event_ledger.jsonl").is_file()
    assert (target / "scripts" / "validate_low_token_workflow.py").is_file()
    assert (target / "scripts" / "validate_source_read_register.py").is_file()
    assert (target / "scripts" / "validate_planned_future_surfaces.py").is_file()
    assert (target / "scripts" / "build_repo_file_index.py").is_file()
    assert (target / "scripts" / "build_command_map.py").is_file()
    assert (target / "scripts" / "query_command_map.py").is_file()
    assert (target / "scripts" / "validate_command_map.py").is_file()
    assert (target / "scripts" / "validate_claude_integration.py").is_file()
    assert (target / "scripts" / "validate_mature_repo_migration_packet.py").is_file()
    assert (target / "scripts" / "validate_release_package.py").is_file()
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
    command_map_summary = run_command(
        [sys.executable, "scripts/build_command_map.py", "--summary-only"],
        cwd=target,
    )
    command_map_query = run_command(
        [
            sys.executable,
            "scripts/query_command_map.py",
            "--safe-read-only",
            "--summary-only",
        ],
        cwd=target,
    )
    command_map_check = run_command(
        [sys.executable, "scripts/validate_command_map.py", "--summary-only"],
        cwd=target,
    )
    claude_check = run_command(
        [sys.executable, "scripts/validate_claude_integration.py", "--summary-only"],
        cwd=target,
    )
    release_check = run_command(
        [sys.executable, "scripts/validate_release_package.py", "--summary-only"],
        cwd=target,
    )
    source_read_check = run_command(
        [sys.executable, "scripts/validate_source_read_register.py", "--summary-only"],
        cwd=target,
    )
    planned_surfaces_check = run_command(
        [sys.executable, "scripts/validate_planned_future_surfaces.py", "--summary-only"],
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
    assert command_map_summary.returncode == 0
    assert command_map_query.returncode == 0
    assert command_map_check.returncode == 0
    assert claude_check.returncode == 0
    assert release_check.returncode == 0
    assert source_read_check.returncode == 0
    assert planned_surfaces_check.returncode == 0
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


def test_bootstrap_can_initialize_git_and_github_remote(tmp_path: Path) -> None:
    target = tmp_path / "tracked-demo"
    remote = "git@github.com:example/tracked-demo.git"
    result = run_command(
        [
            sys.executable,
            str(BOOTSTRAP),
            str(target),
            "--project-name",
            "Tracked Demo",
            "--init-git",
            "--github-remote",
            remote,
            "--git-user-name",
            "Bootstrap Test",
            "--git-user-email",
            "bootstrap@example.invalid",
        ]
    )

    assert result.returncode == 0
    assert (target / ".git").is_dir()
    assert "GIT initialized_git_repo branch=main" in result.stdout
    assert "GIT origin_remote_added" in result.stdout
    assert "GIT initial_commit_created" in result.stdout

    branch = run_command(["git", "branch", "--show-current"], cwd=target)
    remote_check = run_command(["git", "remote", "get-url", "origin"], cwd=target)
    log = run_command(["git", "log", "--oneline", "-1"], cwd=target)
    status = run_command(["git", "status", "--short"], cwd=target)

    assert branch.stdout.strip() == "main"
    assert remote_check.stdout.strip() == remote
    assert "Bootstrap durable slice workflow" in log.stdout
    assert status.stdout.strip() == ""
