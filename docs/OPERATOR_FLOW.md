# Operator Flow

This is the repeatable loop for using the template with an AI agent. The point is
to keep planning, implementation proof, generated refreshes, and closeout
evidence in the repo instead of depending on chat history.

## Slice Loop

Use this loop for each governed slice:

1. Create or update the slice packet with `python scripts/new_slice_packet.py`.
2. Validate the packet with `python scripts/validate_slice_packet.py <packet> --summary-only`.
3. Implement only the owner bundle named in the packet.
4. Validate closeout evidence with `python scripts/validate_slice_closeout.py --mode strict`.
5. When the closeout is durable evidence, record it with `python scripts/validate_slice_closeout.py <closeout> --mode strict --record-ledger --summary-only`.
6. Run `make governance-check`.
7. Run `python scripts/validate_release_package.py --json` before release or template handoff.
8. When the release gate is durable evidence, record it with `python scripts/validate_release_package.py --record-ledger --summary-only`.

## Governance Ledger

Generated refreshes, closeouts, release gates, and external actions must be
represented in `manifests/governance_event_ledger.jsonl` when they become
durable workflow evidence.

Explicit manifest writer commands append generated-refresh ledger events
automatically and skip duplicate event IDs on repeated runs:

- `python scripts/build_repo_file_index.py --write --summary-only`
- `python scripts/build_command_map.py --write --summary-only`
- `python scripts/build_plan_note_index.py --write --summary-only`
- `python scripts/build_artifact_output_map.py --write --summary-only`

Closeout and release gate commands append their own ledger events when explicit
writer intent is present:

- `python scripts/validate_slice_closeout.py <closeout> --mode strict --record-ledger --summary-only`
- `python scripts/validate_release_package.py --record-ledger --summary-only`

Validate ledger integrity with:

```bash
python scripts/validate_governance_event_ledger.py --summary-only
```

## Release Handoff

Before pushing or handing the template to another repo, run:

```bash
make check
make governance-check
make bootstrap-smoke
python scripts/validate_release_package.py --json
git status --short
```

The expected result is passing checks and a clean or intentionally staged
worktree.
