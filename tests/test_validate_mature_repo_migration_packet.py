from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_mature_repo_migration_packet.py"


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path), "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )


def valid_packet() -> dict:
    return {
        "schema_version": "v1.repo_agnostic_mature_repo_migration_packet.1",
        "migration_id": "target_repo_migration",
        "status": "ready",
        "target_repo_path": "/tmp/target-repo",
        "operator_goal": "Adopt selected durable workflow files without replacing existing authority.",
        "adoption_mode": "copy_subset",
        "existing_authority_surfaces": [
            {
                "path": "AGENTS.md",
                "authority_class": "agent_rules",
                "status": "keep",
                "migration_action": "keep",
                "evidence_ref": "AGENTS.md",
            },
            {
                "path": "SKILL.md",
                "authority_class": "skill",
                "status": "keep",
                "migration_action": "keep",
                "evidence_ref": "SKILL.md",
            },
            {
                "path": "README.md",
                "authority_class": "readme",
                "status": "adapt",
                "migration_action": "adapt",
                "evidence_ref": "README.md",
            },
            {
                "path": "pyproject.toml",
                "authority_class": "other",
                "status": "do_not_touch",
                "migration_action": "do_not_touch",
                "evidence_ref": "pyproject.toml",
            },
        ],
        "protected_paths": [
            "AGENTS.md",
            "SKILL.md",
            "pyproject.toml",
            ".github/workflows/",
        ],
        "allowed_mutation_roots": [
            "docs/",
            "plans/",
        ],
        "planned_template_surfaces": [
            {
                "source_path": "PROMPT_FOR_NEW_AGENT.md",
                "target_path": "docs/PROMPT_FOR_NEW_AGENT.md",
                "action": "adapt",
                "overwrite_allowed": False,
                "reason": "Add handoff guidance without replacing target repo rules.",
            }
        ],
        "required_preflight_commands": [
            "git status --short",
            "python -m pytest -q",
        ],
        "validation_commands": [
            (
                "python scripts/validate_mature_repo_migration_packet.py "
                "plans/migration_packet.json --summary-only"
            )
        ],
        "risk_register": [
            "Existing AGENTS.md remains authoritative until exact replacement is approved."
        ],
        "approval": {
            "explicit_operator_approval_required": True,
            "approval_scope": "Approve only the listed planned_template_surfaces paths.",
        },
    }


def write_packet(tmp_path: Path, packet: dict) -> Path:
    path = tmp_path / "migration_packet.json"
    path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    return path


def test_valid_migration_packet_passes(tmp_path: Path) -> None:
    path = write_packet(tmp_path, valid_packet())

    result = run_validator(path)

    assert result.returncode == 0
    assert "PASS mature_repo_migration_packet" in result.stdout


def test_missing_high_risk_authority_fails(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["existing_authority_surfaces"] = [
        item for item in packet["existing_authority_surfaces"] if item["path"] != "AGENTS.md"
    ]
    path = write_packet(tmp_path, packet)

    result = run_validator(path)

    assert result.returncode == 1
    assert "MIGRATION_HIGH_RISK_AUTHORITY_UNCLASSIFIED" in result.stdout


def test_overwrite_protected_path_fails(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["allowed_mutation_roots"].append("AGENTS.md")
    packet["planned_template_surfaces"][0]["target_path"] = "AGENTS.md"
    packet["planned_template_surfaces"][0]["overwrite_allowed"] = True
    path = write_packet(tmp_path, packet)

    result = run_validator(path)

    assert result.returncode == 1
    assert "MIGRATION_TEMPLATE_SURFACE_OVERWRITES_PROTECTED_PATH" in result.stdout


def test_target_must_be_inside_allowed_roots(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["planned_template_surfaces"][0]["target_path"] = "src/PROMPT_FOR_NEW_AGENT.md"
    path = write_packet(tmp_path, packet)

    result = run_validator(path)

    assert result.returncode == 1
    assert "MIGRATION_TEMPLATE_SURFACE_TARGET_OUTSIDE_ALLOWED_ROOT" in result.stdout


def test_full_template_migration_needs_full_approval_scope(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["adoption_mode"] = "full_template_migration"
    packet["approval"]["approval_scope"] = "Approve only selected docs paths."
    path = write_packet(tmp_path, packet)

    result = run_validator(path)

    assert result.returncode == 1
    assert "MIGRATION_FULL_TEMPLATE_APPROVAL_SCOPE_MISSING" in result.stdout
