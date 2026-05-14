from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_release_package.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_release_package", VALIDATOR)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_validator(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, text=True, capture_output=True)


def write_minimal_release_root(tmp_path: Path, *, version: str = "0.4.0") -> Path:
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nname = "demo"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## {version} - 2026-05-14\n",
        encoding="utf-8",
    )
    (tmp_path / ".github" / "workflows" / "check.yml").write_text(
        "\n".join(
            [
                "python-version",
                "3.11",
                "3.12",
                "actions/checkout@v5",
                "actions/setup-python@v6",
                "make check",
                "make bootstrap-smoke",
                "make read-only-check",
            ]
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_current_release_package_passes_summary() -> None:
    result = run_validator([sys.executable, str(VALIDATOR), "--summary-only"])

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == "passed"
    assert payload["required_path_count"] > 20


def test_missing_required_path_fails(tmp_path: Path) -> None:
    module = load_module()
    root = write_minimal_release_root(tmp_path)

    failures = module.validate_release_package(
        root,
        run_subprocess_checks=False,
        required_paths=["README.md"],
        tracked_paths=[],
    )

    assert "RELEASE_REQUIRED_PATH_MISSING path=README.md" in failures


def test_changelog_version_mismatch_fails(tmp_path: Path) -> None:
    module = load_module()
    root = write_minimal_release_root(tmp_path, version="1.2.3")
    (root / "CHANGELOG.md").write_text("# Changelog\n\n## 1.2.2\n", encoding="utf-8")

    failures = module.validate_release_package(
        root,
        run_subprocess_checks=False,
        required_paths=[],
        tracked_paths=[],
    )

    assert "RELEASE_CHANGELOG_VERSION_MISMATCH version=1.2.3" in failures


def test_missing_ci_command_fails(tmp_path: Path) -> None:
    module = load_module()
    root = write_minimal_release_root(tmp_path)
    (root / ".github" / "workflows" / "check.yml").write_text(
        "python-version\n3.11\n3.12\nmake check\n",
        encoding="utf-8",
    )

    failures = module.validate_release_package(
        root,
        run_subprocess_checks=False,
        required_paths=[],
        tracked_paths=[],
    )

    assert "RELEASE_CI_REQUIRED_TEXT_MISSING text=make bootstrap-smoke" in failures


def test_forbidden_release_paths_fail(tmp_path: Path) -> None:
    module = load_module()
    root = write_minimal_release_root(tmp_path)

    failures = module.validate_release_package(
        root,
        run_subprocess_checks=False,
        required_paths=[],
        tracked_paths=[
            "scratch/debug.log",
            "manifests/command_map.json",
            ".env",
        ],
    )

    assert "RELEASE_TRACKED_SCRATCH_OR_CACHE_PATH path=scratch/debug.log" in failures
    assert "RELEASE_TRACKED_GENERATED_MANIFEST path=manifests/command_map.json" in failures
    assert "RELEASE_TRACKED_PRIVATE_OR_SECRET_LIKE_PATH path=.env" in failures
