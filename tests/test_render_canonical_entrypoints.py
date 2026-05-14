from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "scripts" / "render_canonical_entrypoints.py"
METHODOLOGY = ROOT / "repo_agnostic_durable_slice_build_workflow_methodology_20260514.json"


def test_render_check_passes_for_committed_entrypoints() -> None:
    result = subprocess.run(
        [sys.executable, str(RENDERER), "--check"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "PASS entrypoints_match_canonical" in result.stdout


def test_rendered_readme_mentions_realistic_example() -> None:
    methodology = json.loads(METHODOLOGY.read_text(encoding="utf-8"))
    import importlib.util

    spec = importlib.util.spec_from_file_location("render_canonical_entrypoints", RENDERER)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    rendered = module.render_readme(methodology)

    assert "examples/small_config_tool_repo" in rendered
    assert "scripts/render_canonical_entrypoints.py --write" in rendered
    assert "contracts/low_token_workflow_contract.json" in rendered
    assert "scripts/validate_low_token_workflow.py --summary-only" in rendered
