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
        "docs/GLOSSARY.md",
        "docs/TROUBLESHOOTING.md",
        "docs/NEXT_ACTION_DECISION_TREE.md",
        "docs/ANNOTATED_SLICE_PACKET.md",
    ]

    for path in required_paths:
        text = read(path)
        assert len(text.splitlines()) > 20

    start_here = read("START_HERE.md")
    assert "docs/GLOSSARY.md" in start_here
    assert "docs/TROUBLESHOOTING.md" in start_here
    assert "docs/NEXT_ACTION_DECISION_TREE.md" in start_here
    assert "docs/ANNOTATED_SLICE_PACKET.md" in start_here
    assert "PROMPT_FOR_NEW_AGENT.md" in start_here
    assert "RELEASE_CHECKLIST.md" in start_here


def test_new_agent_prompt_is_copy_paste_ready() -> None:
    prompt = read("PROMPT_FOR_NEW_AGENT.md")

    for required_text in [
        "[ABSOLUTE_REPO_PATH]",
        "[ONE OR TWO PARAGRAPHS DESCRIBING WHAT THE REPO SHOULD BUILD]",
        "Read AGENTS.md",
        "plans/repo_roadmap.json",
        "plans/slices/slice_001_packet.json",
        "boundary_rules",
        "refresh_decision",
        "git status --short",
    ]:
        assert required_text in prompt


def test_release_checklist_has_exact_release_commands() -> None:
    checklist = read("RELEASE_CHECKLIST.md")

    for required_text in [
        "make check",
        "make bootstrap-smoke",
        "make read-only-check",
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
    ]:
        assert failure_code in troubleshooting


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
