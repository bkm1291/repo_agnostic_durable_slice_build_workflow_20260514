---
name: durable-slice-release
description: Manual release-readiness workflow for the durable slice template. Use only when the user asks to prepare, check, tag, or publish a release.
argument-hint: "[version or release focus]"
disable-model-invocation: true
---

# Durable Slice Release

Release focus:

```text
$ARGUMENTS
```

Use this only after the user explicitly asks for release work.

## Required Reads

1. Read `RELEASE_CHECKLIST.md`.
2. Read `CHANGELOG.md` and `pyproject.toml`.
3. Read `.github/workflows/check.yml`.
4. Read `CLAUDE.md` and validate Claude Code integration before release.

## Local Checks

Run:

```bash
python scripts/render_canonical_entrypoints.py --check
python scripts/validate_claude_integration.py --summary-only
python scripts/validate_release_package.py --summary-only
make check
make bootstrap-smoke
make read-only-check
git diff --check
git status --short
```

## Release Rules

- Do not tag or publish if generated entrypoints drift.
- Do not tag or publish if release package validation fails.
- Do not tag or publish with unreviewed scratch/cache/private paths.
- Do not push tags or branches unless the user explicitly asks for that release action.

## Closeout

Report exact commands and results, current version, worktree state, whether CI is
expected to pass, and any remaining release blockers.
