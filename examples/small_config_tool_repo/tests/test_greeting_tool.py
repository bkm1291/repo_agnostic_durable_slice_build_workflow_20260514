from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "greeting_config.json"
VALIDATOR = ROOT / "scripts" / "validate_greeting_config.py"
RENDERER = ROOT / "scripts" / "render_greeting.py"


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=False, text=True, capture_output=True)


def test_committed_config_passes_validator() -> None:
    result = run_command([sys.executable, str(VALIDATOR), str(CONFIG), "--summary-only"])

    assert result.returncode == 0
    assert "PASS greeting_config" in result.stdout


def test_renderer_uses_config_owned_values() -> None:
    result = run_command([sys.executable, str(RENDERER), "--config", str(CONFIG)])

    assert result.returncode == 0
    assert result.stdout.strip() == "Hello, workflow operator!"


def test_missing_runtime_value_fails_validation(tmp_path: Path) -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    del config["recipient"]
    bad_config = tmp_path / "bad_config.json"
    bad_config.write_text(json.dumps(config), encoding="utf-8")

    result = run_command([sys.executable, str(VALIDATOR), str(bad_config), "--summary-only"])

    assert result.returncode == 1
    assert "GREETING_CONFIG_MISSING_FIELD field=recipient" in result.stdout


def test_bad_punctuation_fails_validation(tmp_path: Path) -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    config["punctuation"] = "..."
    bad_config = tmp_path / "bad_config.json"
    bad_config.write_text(json.dumps(config), encoding="utf-8")

    result = run_command([sys.executable, str(VALIDATOR), str(bad_config), "--summary-only"])

    assert result.returncode == 1
    assert "GREETING_CONFIG_BAD_PUNCTUATION" in result.stdout
