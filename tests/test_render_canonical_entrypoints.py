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

    assert rendered.index("## What This Is") < rendered.index(
        "## New Here? Start With `START_HERE.md`"
    )
    assert rendered.index("## New Here? Start With `START_HERE.md`") < rendered.index(
        "## Giving This To An Agent? Use `PROMPT_FOR_NEW_AGENT.md`"
    )
    assert rendered.index(
        "## Giving This To An Agent? Use `PROMPT_FOR_NEW_AGENT.md`"
    ) < rendered.index("## 10-Minute Bootstrap Path")
    assert rendered.index("## 10-Minute Bootstrap Path") < rendered.index(
        "## Expert / Custom Path"
    )
    assert "Easiest path" in rendered
    assert "Drag this folder into Claude Code or Codex" in rendered
    assert "Read this folder and use it as the workflow template for my repo" in rendered
    assert "I authorize you to inspect the files in this folder" in rendered
    assert "I authorize you to create that folder if needed" in rendered
    assert "copy or bootstrap this workflow into it" in rendered
    assert "current repo, current folder, current one" in rendered
    assert "use the current working directory as the target" in rendered
    assert "If no target repo path or folder is clear" in rendered
    assert "Do not create app/source implementation files or code features" in rendered
    assert "PROJECT_GOAL.template.md" in rendered
    assert "PROJECT_GOAL.md" in rendered
    assert "No-prompt option" in rendered
    assert "What do you want to build? One or two paragraphs is enough." in rendered
    assert "Do not code until the packet validates" in rendered
    assert "Go. Implement slice 001 exactly as defined" in rendered
    assert "Run the focused validators/tests before closeout." in rendered
    assert "Continue. Pick the next roadmap slice" in rendered
    assert "Do not implement the next slice until I say go." in rendered
    assert "examples/small_config_tool_repo" in rendered
    assert "scripts/render_canonical_entrypoints.py --write" in rendered
    assert "contracts/low_token_workflow_contract.json" in rendered
    assert "scripts/validate_low_token_workflow.py --summary-only" in rendered
    assert "scripts/validate_source_read_register.py --summary-only" in rendered
    assert "scripts/validate_planned_future_surfaces.py --summary-only" in rendered
    assert "scripts/build_repo_file_index.py --summary-only" in rendered
    assert "scripts/build_command_map.py --summary-only" in rendered
    assert "scripts/query_command_map.py --safe-read-only --summary-only" in rendered
    assert "scripts/validate_command_map.py --summary-only" in rendered
    assert "scripts/validate_claude_integration.py --summary-only" in rendered
    assert "CLAUDE.md" in rendered
    assert ".claude/skills/durable-slice/SKILL.md" in rendered
    assert "scripts/validate_read_only_commands.py --summary-only" in rendered
    assert "scripts/validate_release_package.py --summary-only" in rendered
    assert "START_HERE.md" in rendered
    assert "PROMPT_FOR_NEW_AGENT.md" in rendered
    assert "RELEASE_CHECKLIST.md" in rendered
    assert "docs/CI.md" in rendered
    assert "docs/MIGRATING_MATURE_REPO.md" in rendered
    assert "docs/GLOSSARY.md" in rendered
    assert "docs/TROUBLESHOOTING.md" in rendered
    assert "docs/NEXT_ACTION_DECISION_TREE.md" in rendered
    assert "docs/ANNOTATED_SLICE_PACKET.md" in rendered
    assert "plans/source_read_register.json" in rendered
    assert "plans/planned_future_surfaces.json" in rendered
    assert "Schema Vs Validator Authority" in rendered
    assert "validate_mature_repo_migration_packet.py" in rendered


def test_rendered_claude_mentions_project_skills() -> None:
    methodology = json.loads(METHODOLOGY.read_text(encoding="utf-8"))
    import importlib.util

    spec = importlib.util.spec_from_file_location("render_canonical_entrypoints", RENDERER)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    rendered = module.render_claude(methodology)

    assert "@AGENTS.md" in rendered
    assert "START_HERE.md" in rendered
    assert "PROMPT_FOR_NEW_AGENT.md" in rendered
    assert "PROJECT_GOAL.md" in rendered
    assert "/skills" in rendered
    assert "/durable-slice" in rendered
    assert "What do you want to build? One or two paragraphs is enough." in rendered
    assert "Do not create or update a roadmap, packet, or code until the goal is known." in rendered
    assert "Go. Implement slice 001 exactly as defined" in rendered
    assert "Continue. Pick the next roadmap slice" in rendered
    assert ".claude/skills/durable-slice/SKILL.md" in rendered
    assert "validate_claude_integration.py" in rendered


def test_rendered_skill_mentions_project_goal_intake() -> None:
    methodology = json.loads(METHODOLOGY.read_text(encoding="utf-8"))
    import importlib.util

    spec = importlib.util.spec_from_file_location("render_canonical_entrypoints", RENDERER)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    rendered = module.render_skill(methodology)

    assert "## Project Goal Intake" in rendered
    assert "PROJECT_GOAL.md" in rendered
    assert "What do you want to build? One or two paragraphs is enough." in rendered
