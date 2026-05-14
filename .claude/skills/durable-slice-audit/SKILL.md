---
name: durable-slice-audit
description: Read-only audit of a repo using the durable slice workflow. Use when the user asks for comparison, review, score, gap analysis, or whether the workflow is being followed.
argument-hint: "[audit focus]"
context: fork
agent: Explore
---

# Durable Slice Audit

Audit focus:

```text
$ARGUMENTS
```

This is read-only. Do not edit, write, format, regenerate, install, publish, tag,
or mutate files.

## Read Order

1. Read `CLAUDE.md`, `AGENTS.md`, `README.md`, and `START_HERE.md`.
2. Inspect `plans/repo_roadmap.json`, selected slice packets, `plans/source_read_register.json`, and `plans/planned_future_surfaces.json` if present.
3. Use compact checks before broad reads:

```bash
python scripts/render_canonical_entrypoints.py --check
python scripts/build_repo_file_index.py --summary-only
python scripts/build_command_map.py --summary-only
python scripts/query_command_map.py --safe-read-only --summary-only
python scripts/validate_claude_integration.py --summary-only
```

## Audit Questions

- Is the beginner path obvious before expert machinery?
- Are packet owner files, validators, focused tests, boundary rules, and refresh decisions concrete?
- Are generated/index refreshes conditional instead of reflexive?
- Are source-read refs durable instead of chat-only?
- Are Claude Code surfaces present without unsafe default hooks, MCP, or broad tool pre-approval?
- Is release packaging clean of scratch/cache/private paths?

## Output

Lead with findings ordered by severity. Include file paths and exact evidence.
Then give a score from 1-10, residual risks, and the smallest next improvement.
