from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "builder_golden"


def _run(*args: str) -> None:
    r = subprocess.run([sys.executable, *args], cwd=ROOT, check=False, text=True, capture_output=True)
    assert r.returncode == 0, r.stdout + r.stderr


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_builder_outputs_have_stable_contract_headers() -> None:
    _run("scripts/build_repo_file_index.py", "--write", "--summary-only")
    _run("scripts/build_command_map.py", "--write", "--summary-only")
    _run("scripts/build_plan_note_index.py", "--write", "--summary-only")
    _run("scripts/build_artifact_output_map.py", "--write", "--summary-only")

    repo_idx = json.loads((ROOT / "manifests" / "repo_file_index.json").read_text(encoding="utf-8"))
    cmd_map = json.loads((ROOT / "manifests" / "command_map.json").read_text(encoding="utf-8"))
    note_idx = json.loads((ROOT / "manifests" / "plan_note_index.json").read_text(encoding="utf-8"))
    art_map = json.loads((ROOT / "manifests" / "artifact_output_map.json").read_text(encoding="utf-8"))

    assert repo_idx["schema_version"] == "v1.repo_file_index.1"
    assert cmd_map["schema_version"] == "v1.repo_agnostic_command_map.1"
    assert note_idx["schema_version"] == "v1.plan_note_index.1"
    assert art_map["schema_version"] == "v1.artifact_output_map.1"


def test_repo_file_index_exact_fixture(tmp_path: Path) -> None:
    root = tmp_path / "fixture_repo"
    root.mkdir()
    (root / "README.md").write_text("# Demo\n", encoding="utf-8")
    output = root / "manifests" / "repo_file_index.json"

    _run("scripts/build_repo_file_index.py", "--root", str(root), "--output", str(output), "--write", "--summary-only")

    assert json.loads(output.read_text(encoding="utf-8")) == _load_fixture("repo_file_index_expected.json")


def test_command_map_exact_fixture(tmp_path: Path) -> None:
    root = tmp_path / "fixture_repo"
    root.mkdir()
    (root / "pyproject.toml").write_text(
        "\n".join(
            [
                "[tool.durable_slice_workflow.commands]",
                'validate_demo = "python scripts/validate_demo.py --summary-only"',
                'write_demo = "python scripts/write_demo.py --write --summary-only"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    output = root / "manifests" / "command_map.json"

    _run("scripts/build_command_map.py", "--root", str(root), "--output", str(output), "--write", "--summary-only")

    assert json.loads(output.read_text(encoding="utf-8")) == _load_fixture("command_map_expected.json")


def test_plan_note_index_exact_fixture(tmp_path: Path) -> None:
    root = tmp_path / "fixture_repo"
    (root / "plans" / "notes").mkdir(parents=True)
    (root / "scripts").mkdir()
    shutil.copy(ROOT / "scripts" / "validate_plan_notes.py", root / "scripts" / "validate_plan_notes.py")
    shutil.copy(ROOT / "scripts" / "_validator_output.py", root / "scripts" / "_validator_output.py")
    (root / "plans" / "notes" / "plan_note_fixture_20260514.json").write_text(
        json.dumps(
            {
                "schema_version": "v1.plan_note.1",
                "plan_note_id": "plan_note_fixture_20260514",
                "created_at": "2026-05-14T00:00:00Z",
                "status": "active",
                "goal": "Fixture plan note.",
                "next_action": "Run fixture proof.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    output = root / "manifests" / "plan_note_index.json"
    active_output = root / "manifests" / "plan_note_active_set.json"

    _run(
        "scripts/build_plan_note_index.py",
        "--root",
        str(root),
        "--output",
        str(output),
        "--active-output",
        str(active_output),
        "--write",
        "--summary-only",
    )

    assert json.loads(output.read_text(encoding="utf-8")) == _load_fixture("plan_note_index_expected.json")


def test_artifact_output_map_exact_fixture(tmp_path: Path) -> None:
    root = tmp_path / "fixture_repo"
    root.mkdir()
    output = root / "manifests" / "artifact_output_map.json"

    _run("scripts/build_artifact_output_map.py", "--root", str(root), "--output", str(output), "--write", "--summary-only")

    assert json.loads(output.read_text(encoding="utf-8")) == _load_fixture("artifact_output_map_expected.json")
