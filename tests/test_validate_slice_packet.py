from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_slice_packet.py"


def valid_packet() -> dict:
    return {
        "selected_wave_or_slice": "slice_001",
        "goal": "Create the first workflow protocol validator.",
        "files_to_create_or_edit": [
            "scripts/validate_slice_packet.py",
            "tests/test_validate_slice_packet.py",
        ],
        "exact_owner_configs_schemas_contracts": [
            "schemas/slice_packet.schema.json",
            "schemas/refresh_decision.schema.json",
        ],
        "required_source_reads": [
            {
                "surface": "repo-local workflow methodology",
                "read_type": "docs",
                "status": "satisfied",
                "evidence_ref": (
                    "repo_agnostic_durable_slice_build_workflow_methodology_20260514.json"
                ),
            }
        ],
        "owning_wave_validator": "scripts/validate_slice_packet.py",
        "owning_wave_tests": ["tests/test_validate_slice_packet.py"],
        "focused_validators_and_tests": [
            (
                "python scripts/validate_slice_packet.py "
                "plans/slices/slice_001_packet.json --summary-only"
            ),
            "python -m pytest -q tests/test_validate_slice_packet.py",
        ],
        "not_in_scope": [
            "Generated index refresh infrastructure",
            "External provider access",
        ],
        "refresh_decision": {
            "repo_index_required": False,
            "script_import_index_required": False,
            "plan_note_index_required": False,
            "config_variable_inventory_required": False,
            "output_schema_index_required": False,
            "post_output_hook_required": False,
            "next_wave_discovery_depends_on_new_surfaces": False,
            "required_reason": "focused validator and tests directly prove this starter slice",
            "refresh_timing": "skip",
            "decision_basis": [
                "No future slice depends on generated discovery for this starter proof."
            ],
        },
        "commit_plan": {
            "implementation_commit": "source_schema_test_changes_only",
            "generated_refresh_commit": "not_required",
            "do_not_chase_head_only_staleness": True,
        },
    }


def write_packet(tmp_path: Path, packet: dict) -> Path:
    path = tmp_path / "slice_packet.json"
    path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return path


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path), "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )


def directory_snapshot(path: Path) -> dict[str, str]:
    return {
        str(item.relative_to(path)): item.read_text(encoding="utf-8")
        for item in sorted(path.rglob("*"))
        if item.is_file()
    }


def test_valid_minimal_packet_passes(tmp_path: Path) -> None:
    packet_path = write_packet(tmp_path, valid_packet())

    result = run_validator(packet_path)

    assert result.returncode == 0
    assert "PASS slice_packet" in result.stdout


def test_missing_required_field_fails(tmp_path: Path) -> None:
    packet = valid_packet()
    del packet["owning_wave_validator"]
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "PACKET_MISSING_FIELD field=owning_wave_validator" in result.stdout


def test_vague_refresh_reason_fails(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["refresh_decision"]["required_reason"] = "TBD"
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "REFRESH_REASON_VAGUE" in result.stdout


def test_no_refresh_with_non_skip_timing_fails(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["refresh_decision"]["refresh_timing"] = "after_implementation_commit"
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "REFRESH_NOT_REQUIRED_WITH_NON_SKIP_TIMING" in result.stdout


def test_required_refresh_with_skip_timing_fails(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["refresh_decision"]["repo_index_required"] = True
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "REFRESH_REQUIRED_WITH_SKIP_TIMING" in result.stdout


def test_summary_only_does_not_write_files(tmp_path: Path) -> None:
    packet_path = write_packet(tmp_path, valid_packet())
    before = directory_snapshot(tmp_path)

    result = run_validator(packet_path)

    after = directory_snapshot(tmp_path)
    assert result.returncode == 0
    assert after == before


def test_absolute_owner_path_fails(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["files_to_create_or_edit"].append("/tmp/not_repo_relative.py")
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "PACKET_PATH_NOT_REPO_RELATIVE" in result.stdout


def test_duplicate_owner_file_fails(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["files_to_create_or_edit"].append("scripts/validate_slice_packet.py")
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "PACKET_FIELD_DUPLICATE field=files_to_create_or_edit" in result.stdout


def test_source_read_none_must_be_not_required(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["required_source_reads"][0]["read_type"] = "none"
    packet["required_source_reads"][0]["status"] = "satisfied"
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "SOURCE_READ_NONE_STATUS_MISMATCH" in result.stdout


def test_focused_commands_must_reference_owning_validator(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["focused_validators_and_tests"] = [
        "python -m pytest -q tests/test_validate_slice_packet.py"
    ]
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "FOCUSED_COMMANDS_MISSING_OWNING_VALIDATOR" in result.stdout


def test_refresh_required_needs_generated_refresh_commit_plan(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["refresh_decision"]["repo_index_required"] = True
    packet["refresh_decision"]["refresh_timing"] = "after_implementation_commit"
    packet["commit_plan"]["generated_refresh_commit"] = "not_required"
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "COMMIT_PLAN_REFRESH_REQUIRED_BUT_GENERATED_COMMIT_NOT_REQUIRED" in result.stdout


def test_vague_goal_fails(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["goal"] = "TBD"
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "PACKET_FIELD_VAGUE field=goal" in result.stdout


def test_source_read_cannot_use_chat_as_evidence(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["required_source_reads"][0]["evidence_ref"] = "chat"
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "SOURCE_READ_EVIDENCE_CHAT_ONLY" in result.stdout


def test_refresh_required_reason_must_match_flag(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["refresh_decision"]["config_variable_inventory_required"] = True
    packet["refresh_decision"]["refresh_timing"] = "after_implementation_commit"
    packet["refresh_decision"]["required_reason"] = "future discovery needs a fresh artifact map"
    packet["refresh_decision"]["decision_basis"] = ["The next slice needs generated discovery."]
    packet["commit_plan"]["generated_refresh_commit"] = "config_inventory_refresh"
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert (
        "REFRESH_FLAG_REASON_MISSING_KEYWORD field=config_variable_inventory_required"
        in result.stdout
    )


def test_focused_commands_cannot_have_write_intent(tmp_path: Path) -> None:
    packet = valid_packet()
    packet["focused_validators_and_tests"][0] = (
        "python scripts/validate_slice_packet.py "
        "plans/slices/slice_001_packet.json --summary-only --write"
    )
    packet_path = write_packet(tmp_path, packet)

    result = run_validator(packet_path)

    assert result.returncode == 1
    assert "FOCUSED_COMMANDS_CONTAIN_WRITE_INTENT" in result.stdout
