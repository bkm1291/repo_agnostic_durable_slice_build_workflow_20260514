# Next Action Decision Tree

Use this when you are unsure what to do next.

## Start

Run:

```bash
git status --short
```

Then choose the first matching section below.

## The Workflow Was Just Copied

Run the starter checks:

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

If they pass, customize `plans/repo_roadmap.json` and
`plans/slices/slice_001_packet.json` for the real first slice.

## There Is No Roadmap

Create `plans/repo_roadmap.json`.

Keep it small. Name the first slice, its goal, owner area, packet path, and what
is not in scope.

## There Is No Slice Packet

Create `plans/slices/slice_001_packet.json`.

Use `docs/ANNOTATED_SLICE_PACKET.md` as the model.

## The Packet Does Not Validate

Run:

```bash
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
```

Open `docs/TROUBLESHOOTING.md` and fix the first failure.

## The Packet Validates But The Work Feels Too Big

Split the slice.

A slice is too big when you cannot name the owner files, validator, tests, and
not-in-scope boundaries before coding.

## You Need To Find The Right File

Start with file inventory:

```bash
python scripts/build_repo_file_index.py --summary-only
```

If an index has been written:

```bash
python scripts/query_repo_file_index.py --index manifests/repo_file_index.json --path-contains config --summary-only
```

Then read only the exact file or section needed.

## You Are Ready To Implement

Edit only the files named in `files_to_create_or_edit`.

Do not expand the slice silently. If ownership changes, update the packet first.

## Implementation Is Done

Run the focused proof commands named in the packet.

Then run:

```bash
git diff --check
git status --short
```

Commit implementation changes first.

## The Packet Requires Generated Refresh

After the implementation commit, run the exact generated refresh command named
by the repo or packet.

Commit generated outputs separately.

Do not refresh again only because the generated output describes its parent
commit.

## You Still Do Not Know

Stop and write a smaller prep slice. The prep slice should answer exactly one
question, such as:

- which file owns this behavior
- which validator should own proof
- whether a generated refresh is actually needed
- what is explicitly out of scope
