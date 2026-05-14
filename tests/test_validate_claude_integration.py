from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_claude_integration.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_claude_integration", VALIDATOR)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_validator(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args],
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
    )


def copy_claude_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "CLAUDE.md").write_text((ROOT / "CLAUDE.md").read_text(encoding="utf-8"), encoding="utf-8")
    (root / ".gitignore").write_text((ROOT / ".gitignore").read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copytree(ROOT / ".claude", root / ".claude")
    return root


def test_current_claude_integration_passes_summary() -> None:
    result = run_validator(["--summary-only"])

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["status"] == "passed"
    assert payload["skill_count"] == 3


def test_missing_skill_fails(tmp_path: Path) -> None:
    module = load_module()
    root = copy_claude_root(tmp_path)
    (root / ".claude" / "skills" / "durable-slice" / "SKILL.md").unlink()

    failures = module.validate_claude_integration(root)

    assert any("CLAUDE_SKILL_MISSING skill=durable-slice" in item for item in failures)


def test_allowed_tools_frontmatter_fails(tmp_path: Path) -> None:
    module = load_module()
    root = copy_claude_root(tmp_path)
    skill = root / ".claude" / "skills" / "durable-slice" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    skill.write_text(text.replace("argument-hint:", "allowed-tools: Bash\nargument-hint:"), encoding="utf-8")

    failures = module.validate_claude_integration(root)

    assert "CLAUDE_SKILL_ALLOWED_TOOLS_FORBIDDEN skill=durable-slice" in failures


def test_default_hooks_and_mcp_fail(tmp_path: Path) -> None:
    module = load_module()
    root = copy_claude_root(tmp_path)
    (root / ".mcp.json").write_text('{"mcpServers": {}}\n', encoding="utf-8")
    (root / ".claude" / "settings.json").write_text('{"hooks": {"PreToolUse": []}}\n', encoding="utf-8")

    failures = module.validate_claude_integration(root)

    assert "CLAUDE_DEFAULT_MCP_FORBIDDEN path=.mcp.json" in failures
    assert "CLAUDE_DEFAULT_HOOKS_FORBIDDEN path=.claude/settings.json" in failures


def test_gitignore_must_exclude_local_claude_state(tmp_path: Path) -> None:
    module = load_module()
    root = copy_claude_root(tmp_path)
    (root / ".gitignore").write_text("*.log\n", encoding="utf-8")

    failures = module.validate_claude_integration(root)

    assert "CLAUDE_GITIGNORE_REQUIRED_TEXT_MISSING text=CLAUDE.local.md" in failures
    assert "CLAUDE_GITIGNORE_REQUIRED_TEXT_MISSING text=.claude/settings.local.json" in failures
