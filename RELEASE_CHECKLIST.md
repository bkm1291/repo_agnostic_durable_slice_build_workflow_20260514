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
python scripts/validate_read_only_commands.py --summary-only
make check
make bootstrap-smoke
make read-only-check
git diff --check
git status --short
```

The expected result is no command failure. `git status --short` should show only
intentional release changes.

## 3. Inspect The Release Diff

```bash
git diff --stat
git diff -- README.md START_HERE.md PROMPT_FOR_NEW_AGENT.md RELEASE_CHECKLIST.md CHANGELOG.md
```

Confirm the public entrypoints explain the current workflow and no generated
entrypoint drift remains.

## 4. Commit

```bash
git add .
git commit -m "Release vX.Y.Z"
git status --short
```

`git status --short` should be clean after the commit.

## 5. Tag

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git tag --list 'v*' --sort=-creatordate | head
```

## 6. Publish

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

## 7. Smoke A Fresh Consumer Copy

```bash
python scripts/bootstrap_local_repo.py /tmp/durable-slice-release-consumer --project-name durable-slice-release-consumer --force
cd /tmp/durable-slice-release-consumer
python scripts/render_canonical_entrypoints.py --check
python scripts/validate_low_token_workflow.py --summary-only
python scripts/validate_source_read_register.py --summary-only
python scripts/validate_planned_future_surfaces.py --summary-only
python scripts/build_repo_file_index.py --summary-only
python scripts/validate_read_only_commands.py --summary-only
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
python -m pytest -q tests
```

## 8. Release Note

Use this shape:

```text
vX.Y.Z

- What changed:
- Who should use it:
- Validation:
  - make check
  - make bootstrap-smoke
  - make read-only-check
- Known limitations:
```
