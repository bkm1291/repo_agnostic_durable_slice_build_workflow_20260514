# Release Checklist

Use this before tagging or publishing the template.

Replace `vX.Y.Z` with the release version.

## 1. Confirm The Version

```bash
rg -n 'version = "|## ' pyproject.toml CHANGELOG.md
```

Confirm `pyproject.toml` and `CHANGELOG.md` agree.

## 2. Run Full Local Validation

```bash
python scripts/render_canonical_entrypoints.py --check
python scripts/validate_low_token_workflow.py --summary-only
python scripts/validate_source_read_register.py --summary-only
python scripts/validate_planned_future_surfaces.py --summary-only
python scripts/build_repo_file_index.py --summary-only
python scripts/build_command_map.py --summary-only
python scripts/query_command_map.py --safe-read-only --summary-only
python scripts/validate_command_map.py --summary-only
python scripts/validate_read_only_commands.py --summary-only
python scripts/validate_release_package.py --summary-only
make check
make bootstrap-smoke
make read-only-check
git diff --check
git status --short
```

The expected result is no command failure. `git status --short` should show only
intentional release changes.

## 3. Confirm CI Configuration

```bash
python - <<'PY'
from pathlib import Path
path = Path(".github/workflows/check.yml")
text = path.read_text(encoding="utf-8")
required = [
    "python-version",
    "3.11",
    "3.12",
    "actions/checkout@v5",
    "actions/setup-python@v6",
    "make check",
    "make bootstrap-smoke",
    "make read-only-check",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f"missing CI checks: {missing}")
print("CI workflow present")
PY
```

After pushing, confirm the GitHub Actions `check` workflow passes on `main`.

## 4. Inspect The Release Diff

```bash
git diff --stat
git diff -- README.md START_HERE.md PROMPT_FOR_NEW_AGENT.md RELEASE_CHECKLIST.md CHANGELOG.md .github/workflows/check.yml
```

Confirm the public entrypoints explain the current workflow and no generated
entrypoint drift remains.

## 5. Commit

```bash
git add .
git commit -m "Release vX.Y.Z"
git status --short
```

`git status --short` should be clean after the commit.

## 6. Tag

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git tag --list 'v*' --sort=-creatordate | head
```

## 7. Publish

Check the remote first:

```bash
git remote -v
git branch --show-current
```

Push only when the remote and branch are correct:

```bash
git push origin HEAD
git push origin vX.Y.Z
```

## 8. Smoke A Fresh Consumer Copy

```bash
python scripts/bootstrap_local_repo.py /tmp/durable-slice-release-consumer --project-name durable-slice-release-consumer --force
cd /tmp/durable-slice-release-consumer
python scripts/render_canonical_entrypoints.py --check
python scripts/validate_low_token_workflow.py --summary-only
python scripts/validate_source_read_register.py --summary-only
python scripts/validate_planned_future_surfaces.py --summary-only
python scripts/build_repo_file_index.py --summary-only
python scripts/build_command_map.py --summary-only
python scripts/query_command_map.py --safe-read-only --summary-only
python scripts/validate_command_map.py --summary-only
python scripts/validate_read_only_commands.py --summary-only
python scripts/validate_release_package.py --summary-only
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
python -m pytest -q tests
```

## 9. Release Note

Use this shape:

```text
vX.Y.Z

- What changed:
- Who should use it:
- Validation:
  - make check
  - make bootstrap-smoke
  - make read-only-check
  - GitHub Actions check
- Known limitations:
```
