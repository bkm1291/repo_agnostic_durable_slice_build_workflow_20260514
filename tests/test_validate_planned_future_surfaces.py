from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_planned_future_surfaces.py"
REGISTRY = ROOT / "plans" / "planned_future_surfaces.json"


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path), "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )


def base_registry() -> dict:
    return {
        "schema_version": "v1.repo_agnostic_planned_future_surfaces.1",
        "registry_id": "test_planned_future_surfaces",
        "status": "active",
        "purpose": "Classify intentionally absent future files.",
        "surfaces": [
            {
                "surface_id": "config_inventory",
                "path": "manifests/config_inventory.json",
                "surface_type": "generated_index",
                "status": "planned_not_created",
                "owner_slice": "slice_002",
                "activation_packet": "plans/slices/slice_002_packet.json",
                "reason": "Created only after multiple runtime configs exist.",
            }
        ],
    }


def write_registry(tmp_path: Path, registry: dict) -> Path:
    path = tmp_path / "planned_future_surfaces.json"
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return path


def test_default_planned_future_surfaces_validates() -> None:
    result = run_validator(REGISTRY)

    assert result.returncode == 0
    assert "PASS planned_future_surfaces" in result.stdout


def test_duplicate_surface_id_fails(tmp_path: Path) -> None:
    registry = base_registry()
    registry["surfaces"].append(dict(registry["surfaces"][0]))
    registry["surfaces"][1]["path"] = "manifests/other.json"
    path = write_registry(tmp_path, registry)

    result = run_validator(path)

    assert result.returncode == 1
    assert "PLANNED_SURFACE_DUPLICATE_ID" in result.stdout


def test_absolute_surface_path_fails(tmp_path: Path) -> None:
    registry = base_registry()
    registry["surfaces"][0]["path"] = "/tmp/config_inventory.json"
    path = write_registry(tmp_path, registry)

    result = run_validator(path)

    assert result.returncode == 1
    assert "PLANNED_SURFACE_BAD_PATH" in result.stdout
