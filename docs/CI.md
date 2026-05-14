# CI

The public template uses GitHub Actions to prove that the copied workflow still
works on supported Python versions.

## Workflow

The workflow file is:

```text
.github/workflows/check.yml
```

It runs on:

- `push`
- `pull_request`

It uses:

- `actions/checkout@v5`
- `actions/setup-python@v6`
- Python `3.11`
- Python `3.12`

## Required Commands

The workflow must run:

```bash
make check
make bootstrap-smoke
make read-only-check
```

`make check` proves generated entrypoints, low-token policy, planned-future
surfaces, command-map discovery, examples, tests, JSON/TOML parsing, and release
package sanity.

`make bootstrap-smoke` proves a fresh consumer copy can validate itself.

`make read-only-check` proves declared status commands do not modify files or
print secret-like output.

## Release Rule

Before tagging or publishing, run the local checklist in `RELEASE_CHECKLIST.md`
and confirm the GitHub Actions `check` workflow passed on `main`.

If CI fails, fix the first failing command locally before changing the workflow.

## New Repo Tracking

For a new repo that should be tracked from the start, bootstrap with git enabled:

```bash
python scripts/bootstrap_local_repo.py ../my-new-repo --project-name my-new-repo --init-git --github-remote git@github.com:<owner>/<repo>.git
```

Run the starter checks locally before pushing:

```bash
make check
make bootstrap-smoke
make read-only-check
git status --short
git push -u origin main
```

The first push should contain the validated bootstrap governance commit. Later
slices should keep implementation commits, generated-refresh commits, and
meaningful closeout evidence commits separate.
