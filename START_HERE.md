# Start Here

This template helps you start a repo in small slices that can be understood
later without reading old chat.

Use it when you want a new repo to have:

- a roadmap for what will be built
- one small packet per piece of work
- a validator and focused tests for each piece
- a clear rule for when generated indexes or reports should refresh
- a copy-paste prompt for handing the repo to a fresh agent
- a release checklist for tagging or publishing

## First 30 Minutes

### 1. Bootstrap A New Repo

From this template repo:

```bash
python scripts/bootstrap_local_repo.py ../my-new-repo --project-name my-new-repo
cd ../my-new-repo
```

The bootstrap copies the workflow files, starter scripts, tests, examples, and a
starter roadmap/packet.

### 2. Run The Starter Checks

```bash
python scripts/render_canonical_entrypoints.py --check
python scripts/validate_low_token_workflow.py --summary-only
python scripts/validate_source_read_register.py --summary-only
python scripts/validate_planned_future_surfaces.py --summary-only
python scripts/build_repo_file_index.py --summary-only
python scripts/validate_read_only_commands.py --summary-only
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
python -m pytest -q tests
```

If these pass, the workflow copied correctly.

### 3. Read Three Files

Read these before changing the new repo:

- `README.md`: the short workflow overview
- `plans/repo_roadmap.json`: the current work plan
- `plans/slices/slice_001_packet.json`: the first slice packet

Use `docs/GLOSSARY.md` if a term is unfamiliar.

### 4. Pick The Smallest First Slice

A good first slice is small enough to name all of this before coding:

- the files you will create or edit
- the config, schema, or contract that owns the behavior
- the validator that checks the behavior
- the focused tests that prove the behavior
- what is not in scope
- the machine-checkable boundary rules

If you cannot name those, split the work smaller.

### 5. Edit The Packet First

Update `plans/slices/slice_001_packet.json` before editing source code.
If the packet cites `source_read:<id>` or a planned future surface id, update
`plans/source_read_register.json` or `plans/planned_future_surfaces.json` first.

Then run:

```bash
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
```

Fix packet failures before implementation.

### 6. Build Only What The Packet Owns

Edit only the files listed in `files_to_create_or_edit`.

Add or update the validator named in `owning_wave_validator`.

Add or update the tests named in `owning_wave_tests`.

### 7. Prove The Slice

Run the commands listed in `focused_validators_and_tests`.

For most starter repos, this will look like:

```bash
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
python -m pytest -q tests
git diff --check
git status --short
```

### 8. Commit The Implementation

Commit source/config/test/docs changes first.

Only refresh generated indexes afterward if the packet says a refresh is needed.

## What To Do When Stuck

- If a term is unclear, read `docs/GLOSSARY.md`.
- If a validator fails, read `docs/TROUBLESHOOTING.md`.
- If you do not know the next action, read `docs/NEXT_ACTION_DECISION_TREE.md`.
- If the packet fields feel abstract, read `docs/ANNOTATED_SLICE_PACKET.md`.
- If you are handing this repo to a fresh agent, fill in `PROMPT_FOR_NEW_AGENT.md`.
- If you are tagging or publishing, follow `RELEASE_CHECKLIST.md`.
