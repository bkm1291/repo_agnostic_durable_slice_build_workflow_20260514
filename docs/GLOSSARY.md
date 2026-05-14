# Glossary

## Roadmap

The durable plan for the repo. It says what slices exist, what order they should
happen in, and what each slice is trying to prove.

Starter path: `plans/repo_roadmap.json`

## Slice

One small piece of work. A slice should be small enough that the files, proof,
tests, and out-of-scope boundaries are clear before coding.

## Slice Packet

The checklist for one slice. It tells the worker what to edit, what to read,
what validator owns the behavior, what focused tests prove it, and whether any
generated indexes need refresh.

Starter path: `plans/slices/slice_001_packet.json`

## Owner Files

The files a slice is allowed to create or edit. These live in
`files_to_create_or_edit`.

If a needed file is missing from the list, update the packet first.

## Owner Config, Schema, Or Contract

The durable file that owns a behavior or rule.

Examples:

- a JSON config that owns runtime values
- a JSON schema that owns data shape
- a contract file that owns workflow rules

## Required Source Reads

The exact files, docs, indexes, or local references that must be read before the
slice is safe to implement.

Chat memory is not durable evidence. Prefer repo files and compact indexes.

## Source-Read Register

A durable list of exact source or documentation reads that packets can cite with
`source_read:<id>`.

Starter path: `plans/source_read_register.json`

Use:

```bash
python scripts/validate_source_read_register.py --summary-only
```

## Planned Future Surfaces

A registry of files that are intentionally planned for later slices. This helps
future workers distinguish "not built yet on purpose" from "missing by mistake".

Starter path: `plans/planned_future_surfaces.json`

Use:

```bash
python scripts/validate_planned_future_surfaces.py --summary-only
```

## Boundary Rules

Machine-checkable slice limits. Boundary rules name allowed scope, forbidden path
prefixes, forbidden keywords, and planned future surfaces that must not be built
in the current slice.

## Owning Validator

The script that checks the rule or behavior owned by the slice.

Example:

```bash
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
```

## Focused Tests

The tests that prove the slice behavior directly. Broad checks are useful, but
focused tests are the main proof.

## Refresh Decision

The packet section that says whether generated discovery files, indexes,
inventories, or post-output hooks need to run after implementation.

If no future work depends on fresh generated discovery, the refresh timing
should usually be `skip`.

## Generated Refresh

A deliberate update to generated indexes, maps, manifests, dashboards, or other
derived files.

Implementation changes should be committed before generated refresh changes.

## Head-Only Staleness

A generated index may describe the commit before the generated-index commit.
That alone is not a reason to refresh again.

## Low-Token Workflow

The habit of finding the right file or section before reading broadly.

Default pattern:

1. query or inspect file inventory
2. read only the exact relevant section
3. run compact validators
4. stop

## File Inventory

A compact list of repo files, types, sizes, line counts, and hashes.

Use:

```bash
python scripts/build_repo_file_index.py --summary-only
```

## Command Map

A compact list of repo commands, helpers, validators, builders, writers, test
commands, side-effect classes, compact modes, owner refs, validator refs, and
focused test refs.

Use:

```bash
python scripts/build_command_map.py --summary-only
python scripts/query_command_map.py --safe-read-only --summary-only
python scripts/validate_command_map.py --summary-only
```

## Release Package Validator

A read-only release sanity check for required public files, generated entrypoint
drift, examples, CI commands, version/changelog agreement, and tracked
scratch/cache/private path names.

Use:

```bash
python scripts/validate_release_package.py --summary-only
```

## Schema-Vs-Validator Authority

Schemas define JSON shape, required fields, allowed enum values, and portable
structural constraints.

Python validators define semantic rules, cross-file rules, side-effect rules,
read-only checks, and local adoption safety.

If a schema accepts a document but the Python validator rejects it, the
validator rejection blocks closeout until the schema or document is
intentionally updated.

## Mature Repo Migration Packet

A required adoption packet for using this template in an existing repo that
already has its own authority surfaces.

Use:

```bash
python scripts/validate_mature_repo_migration_packet.py <packet> --summary-only
```

## Read-Only Command Harness

A validator that can check or run selected status commands and prove they did
not change files.

Use:

```bash
python scripts/validate_read_only_commands.py --summary-only
python scripts/validate_read_only_commands.py --run --summary-only
```
