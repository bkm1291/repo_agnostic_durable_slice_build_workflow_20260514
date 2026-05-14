#!/usr/bin/env python3
"""Validate Claude Code entrypoints and project skills for this template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CLAUDE_MD = Path("CLAUDE.md")
MCP_JSON = Path(".mcp.json")
CLAUDE_SETTINGS = Path(".claude/settings.json")
REQUIRED_SKILLS = {
    "durable-slice": {
        "path": Path(".claude/skills/durable-slice/SKILL.md"),
        "required_body": [
            "START_HERE.md",
            "plans/slices/slice_001_packet.json",
            "PROJECT_GOAL.md",
            "validate_slice_packet.py",
            "validate_claude_integration.py",
            "What do you want to build? One or two paragraphs is enough.",
            "Do not create or update a roadmap, packet, or code until the goal is known.",
        ],
    },
    "durable-slice-audit": {
        "path": Path(".claude/skills/durable-slice-audit/SKILL.md"),
        "required_frontmatter": {
            "context": "fork",
            "agent": "Explore",
        },
        "required_body": [
            "read-only",
            "validate_claude_integration.py",
            "$ARGUMENTS",
        ],
    },
    "durable-slice-release": {
        "path": Path(".claude/skills/durable-slice-release/SKILL.md"),
        "required_frontmatter": {
            "disable-model-invocation": True,
        },
        "required_body": [
            "RELEASE_CHECKLIST.md",
            "validate_release_package.py",
            "validate_claude_integration.py",
        ],
    },
}

CLAUDE_MD_REQUIRED_TEXT = (
    "@AGENTS.md",
    "START_HERE.md",
    "PROMPT_FOR_NEW_AGENT.md",
    "PROJECT_GOAL.md",
    "validate_slice_packet.py",
    "validate_claude_integration.py",
    "/skills",
    "/durable-slice",
    ".claude/skills/durable-slice/SKILL.md",
    "What do you want to build? One or two paragraphs is enough.",
    "Do not create or update a roadmap, packet, or code until the goal is known.",
)

GITIGNORE_REQUIRED_TEXT = (
    "CLAUDE.local.md",
    ".claude/settings.local.json",
)


def _frontmatter(path: Path) -> tuple[dict[str, Any], str, list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, ["CLAUDE_SKILL_FRONTMATTER_MISSING"]

    end_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}, text, ["CLAUDE_SKILL_FRONTMATTER_UNCLOSED"]

    parsed: dict[str, Any] = {}
    failures: list[str] = []
    for raw_line in lines[1:end_index]:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            failures.append(f"CLAUDE_SKILL_FRONTMATTER_INVALID_LINE line={line}")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if value.lower() == "true":
            parsed[key] = True
        elif value.lower() == "false":
            parsed[key] = False
        else:
            parsed[key] = value
    body = "\n".join(lines[end_index + 1 :])
    return parsed, body, failures


def _load_json_if_present(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.exists():
        return None, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"CLAUDE_SETTINGS_INVALID_JSON path={path} line={exc.lineno}"]
    if not isinstance(data, dict):
        return None, [f"CLAUDE_SETTINGS_NOT_OBJECT path={path}"]
    return data, []


def _validate_claude_md(root: Path) -> list[str]:
    path = root / CLAUDE_MD
    if not path.exists():
        return [f"CLAUDE_ENTRYPOINT_MISSING path={CLAUDE_MD}"]
    text = path.read_text(encoding="utf-8")
    failures = [
        f"CLAUDE_ENTRYPOINT_REQUIRED_TEXT_MISSING text={item}"
        for item in CLAUDE_MD_REQUIRED_TEXT
        if item not in text
    ]
    if len(text.splitlines()) > 200:
        failures.append(f"CLAUDE_ENTRYPOINT_TOO_LONG lines={len(text.splitlines())}")
    return failures


def _validate_skill(root: Path, skill_name: str, expected: dict[str, Any]) -> list[str]:
    relative = expected["path"]
    path = root / relative
    if not path.exists():
        return [f"CLAUDE_SKILL_MISSING skill={skill_name} path={relative}"]

    frontmatter, body, failures = _frontmatter(path)
    if frontmatter.get("name") != skill_name:
        failures.append(
            f"CLAUDE_SKILL_NAME_MISMATCH skill={skill_name} actual={frontmatter.get('name')}"
        )
    description = frontmatter.get("description")
    if not isinstance(description, str) or len(description.strip()) < 20:
        failures.append(f"CLAUDE_SKILL_DESCRIPTION_MISSING skill={skill_name}")
    if "allowed-tools" in frontmatter:
        failures.append(f"CLAUDE_SKILL_ALLOWED_TOOLS_FORBIDDEN skill={skill_name}")

    for key, value in expected.get("required_frontmatter", {}).items():
        if frontmatter.get(key) != value:
            failures.append(
                f"CLAUDE_SKILL_FRONTMATTER_VALUE_MISMATCH skill={skill_name} key={key}"
            )
    for item in expected.get("required_body", []):
        if item not in body:
            failures.append(
                f"CLAUDE_SKILL_REQUIRED_TEXT_MISSING skill={skill_name} text={item}"
            )
    return failures


def _validate_default_no_surprise_config(root: Path) -> list[str]:
    failures: list[str] = []
    if (root / MCP_JSON).exists():
        failures.append(f"CLAUDE_DEFAULT_MCP_FORBIDDEN path={MCP_JSON}")

    settings, settings_failures = _load_json_if_present(root / CLAUDE_SETTINGS)
    failures.extend(settings_failures)
    if settings:
        if "hooks" in settings:
            failures.append(f"CLAUDE_DEFAULT_HOOKS_FORBIDDEN path={CLAUDE_SETTINGS}")
        permissions = settings.get("permissions")
        if isinstance(permissions, dict) and permissions.get("allow"):
            failures.append(
                f"CLAUDE_DEFAULT_PERMISSION_ALLOW_FORBIDDEN path={CLAUDE_SETTINGS}"
            )
    return failures


def _validate_gitignore(root: Path) -> list[str]:
    path = root / ".gitignore"
    if not path.exists():
        return ["CLAUDE_GITIGNORE_MISSING"]
    text = path.read_text(encoding="utf-8")
    return [
        f"CLAUDE_GITIGNORE_REQUIRED_TEXT_MISSING text={item}"
        for item in GITIGNORE_REQUIRED_TEXT
        if item not in text
    ]


def validate_claude_integration(root: Path) -> list[str]:
    root = root.resolve()
    failures: list[str] = []
    failures.extend(_validate_claude_md(root))
    for skill_name, expected in REQUIRED_SKILLS.items():
        failures.extend(_validate_skill(root, skill_name, expected))
    failures.extend(_validate_default_no_surprise_config(root))
    failures.extend(_validate_gitignore(root))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args(argv)

    failures = validate_claude_integration(args.root)
    if failures:
        if args.summary_only:
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "failure_count": len(failures),
                        "failures": failures,
                    }
                )
            )
        else:
            print(f"FAIL claude_integration root={args.root} failures={len(failures)}")
            for failure in failures:
                print(failure)
        return 1

    payload = {
        "status": "passed",
        "skill_count": len(REQUIRED_SKILLS),
        "entrypoint": CLAUDE_MD.as_posix(),
    }
    if args.summary_only:
        print(json.dumps(payload))
    else:
        print(
            "PASS claude_integration "
            f"root={args.root} "
            f"skills={payload['skill_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
