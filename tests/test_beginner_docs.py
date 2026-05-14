from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_beginner_docs_exist_and_cross_link() -> None:
    required_paths = [
        "START_HERE.md",
        "PROMPT_FOR_NEW_AGENT.md",
        "RELEASE_CHECKLIST.md",
        "CLAUDE.md",
        ".claude/skills/durable-slice/SKILL.md",
        ".claude/skills/durable-slice-audit/SKILL.md",
        ".claude/skills/durable-slice-release/SKILL.md",
        "docs/CI.md",
        "docs/GLOSSARY.md",
        "docs/MIGRATING_MATURE_REPO.md",
        "docs/TROUBLESHOOTING.md",
        "docs/NEXT_ACTION_DECISION_TREE.md",
        "docs/ANNOTATED_SLICE_PACKET.md",
    ]

    for path in required_paths:
        text = read(path)
        assert len(text.splitlines()) > 20

    project_goal_template = read("PROJECT_GOAL.template.md")
    assert "PROJECT_GOAL.md" in project_goal_template
    assert "What do you want to build? One or two paragraphs is enough." in project_goal_template
    assert "Do not create or update a roadmap, packet, or code until the goal is known." in project_goal_template

    start_here = read("START_HERE.md")
    assert "PROJECT_GOAL.template.md" in start_here
    assert "PROJECT_GOAL.md" in start_here
    assert "No-prompt option" in start_here
    assert "Read this folder and use it as the workflow template for my repo" in start_here
    assert "I authorize you to inspect the files in this folder" in start_here
    assert "I authorize you to create that folder if needed" in start_here
    assert "copy or bootstrap this workflow into it" in start_here
    assert "current repo, current folder, current one" in start_here
    assert "use the current working directory as the target" in start_here
    assert "docs/GLOSSARY.md" in start_here
    assert "docs/TROUBLESHOOTING.md" in start_here
    assert "docs/CI.md" in start_here
    assert "docs/NEXT_ACTION_DECISION_TREE.md" in start_here
    assert "docs/ANNOTATED_SLICE_PACKET.md" in start_here
    assert "PROMPT_FOR_NEW_AGENT.md" in start_here
    assert "CLAUDE.md" in start_here
    assert "/durable-slice" in start_here
    assert "drag this folder into" in start_here
    assert "Claude Code or Codex" in start_here
    assert "Do not code until the packet validates" in start_here
    assert "Paste this into your prompt box:" in start_here
    assert "Go. Implement slice 001 exactly as defined" in start_here
    assert "Continue. Inspect plans/repo_roadmap.json" in start_here
    assert "RELEASE_CHECKLIST.md" in start_here
    assert "docs/MIGRATING_MATURE_REPO.md" in start_here


def test_new_agent_prompt_is_copy_paste_ready() -> None:
    prompt = read("PROMPT_FOR_NEW_AGENT.md")

    for required_text in [
        "Shortest beginner prompt",
        "Read this folder and use it as the workflow template for my repo",
        "I authorize you to inspect the files in this folder",
        "I authorize you to create that folder if needed",
        "copy or bootstrap this workflow into it",
        "current repo, current folder, current one",
        "use the current working directory as the target",
        "Do not create app/source implementation files or code features",
        "PROJECT_GOAL.template.md",
        "PROJECT_GOAL.md",
        "What do you want to build? One or two paragraphs is enough.",
        "use it automatically",
        "Do not create or update a roadmap, packet, or code until the goal is known.",
        "Do not code until the packet validates",
        "Paste this into your prompt box:",
        "Go. Implement slice 001 exactly as defined",
        "Run the focused validators/tests before closeout.",
        "Continue. Inspect plans/repo_roadmap.json",
        "owner files, owner configs/schemas/contracts",
        "Do not implement the next slice until I say go.",
        "[ABSOLUTE_REPO_PATH]",
        "[ONE OR TWO PARAGRAPHS DESCRIBING WHAT THE REPO SHOULD BUILD]",
        "Read AGENTS.md",
        "Read CLAUDE.md",
        "/durable-slice",
        "validate_claude_integration.py",
        "plans/repo_roadmap.json",
        "plans/slices/slice_001_packet.json",
        "boundary_rules",
        "refresh_decision",
        "build_command_map.py",
        "query_command_map.py",
        "MIGRATING_MATURE_REPO.md",
        "git status --short",
    ]:
        assert required_text in prompt


def test_release_checklist_has_exact_release_commands() -> None:
    checklist = read("RELEASE_CHECKLIST.md")

    for required_text in [
        "make check",
        "make bootstrap-smoke",
        "make read-only-check",
        "build_command_map.py",
        "query_command_map.py",
        "validate_claude_integration.py",
        "validate_release_package.py",
        "git diff --check",
        "git commit -m",
        "git tag -a",
        "git push origin HEAD",
        "git push origin vX.Y.Z",
    ]:
        assert required_text in checklist


def test_troubleshooting_mentions_validator_failure_codes() -> None:
    troubleshooting = read("docs/TROUBLESHOOTING.md")

    for failure_code in [
        "PACKET_MISSING_FIELD",
        "PACKET_FIELD_VAGUE",
        "SOURCE_READ_EVIDENCE_CHAT_ONLY",
        "SOURCE_READ_REGISTER_REF_NOT_FOUND",
        "BOUNDARY_FORBIDDEN_PATH_PREFIX_MATCH",
        "REFRESH_REQUIRED_WITH_SKIP_TIMING",
        "READ_ONLY_COMMAND_MODIFIED_PATHS",
        "READ_ONLY_COMMAND_SECRET_OUTPUT",
        "COMMAND_MAP_WRITER_WITHOUT_EXPLICIT_INTENT",
        "CLAUDE_ENTRYPOINT_REQUIRED_TEXT_MISSING",
        "CLAUDE_SKILL_ALLOWED_TOOLS_FORBIDDEN",
        "CLAUDE_DEFAULT_HOOKS_FORBIDDEN",
        "CLAUDE_DEFAULT_MCP_FORBIDDEN",
        "MIGRATION_HIGH_RISK_AUTHORITY_UNCLASSIFIED",
        "RELEASE_REQUIRED_PATH_MISSING",
    ]:
        assert failure_code in troubleshooting


def test_mature_repo_migration_doc_explains_guardrails() -> None:
    migration_doc = read("docs/MIGRATING_MATURE_REPO.md")

    for required_text in [
        "validate_mature_repo_migration_packet.py",
        "existing_authority_surfaces",
        "protected_paths",
        "adoption_mode",
        "Schema-Vs-Validator Authority",
    ]:
        assert required_text in migration_doc


def test_annotated_packet_covers_required_fields() -> None:
    annotated = read("docs/ANNOTATED_SLICE_PACKET.md")

    for field in [
        "selected_wave_or_slice",
        "goal",
        "files_to_create_or_edit",
        "exact_owner_configs_schemas_contracts",
        "required_source_reads",
        "owning_wave_validator",
        "owning_wave_tests",
        "focused_validators_and_tests",
        "not_in_scope",
        "boundary_rules",
        "refresh_decision",
        "commit_plan",
    ]:
        assert f"`{field}`" in annotated or f'"{field}"' in annotated
