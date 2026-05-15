# Changelog

All notable changes to this local template are documented here.

## Unreleased

- Added governance event ledger documentation to the generated README, `START_HERE.md`, `docs/OPERATOR_FLOW.md`, and release checklist.
- Documented `make governance-check` as the main workflow health gate for plan notes, maps, closeout, lifecycle, secrets, provenance, receipts/checkpoints, and ledger integrity.
- Clarified that manifest writer commands append generated-refresh ledger events automatically and skip duplicate event IDs.
- Added explicit closeout and release-gate ledger writer modes with idempotent event recording.

## 0.4.0 - 2026-05-14

- Added source-read/full-read register, schema, validator, and tests.
- Added planned-future-surfaces registry, schema, validator, and tests.
- Added packet `boundary_rules` validation for allowed scope, forbidden path prefixes, forbidden keywords, and deferred future-surface refs.
- Hardened the read-only command harness with git porcelain before/after comparison and secret-like stdout/stderr scanning.
- Added `PROMPT_FOR_NEW_AGENT.md` for non-expert handoff to a fresh agent.
- Added `RELEASE_CHECKLIST.md` with exact local validation, tag, and publish commands.
- Added GitHub Actions CI for Python 3.11 and 3.12 running `make check`, `make bootstrap-smoke`, and `make read-only-check`.
- Added command-map contract, schema, builder, validator, and tests for durable command/helper discovery.
- Added mature-repo migration guide, packet schema, validator, and tests to prevent unsafe adoption into existing repos.
- Added a first-class schema-vs-Python-validator authority rule.
- Added release package validation for public-file completeness, CI command coverage, example validation, and tracked scratch/cache/private path checks.
- Added command-map query support for beginner-friendly command discovery without reading the full map.
- Expanded planned-future-surface registry coverage for validator, test, and schema/contract maps.
- Wired the new hardening into bootstrap, examples, docs, generated entrypoints, Makefile checks, and publish metadata.

## 0.3.0 - 2026-05-14

- Added `START_HERE.md` with a first-30-minutes beginner walkthrough.
- Added glossary, troubleshooting, next-action decision tree, and annotated slice-packet docs.
- Wired beginner docs into canonical methodology metadata, generated README, pyproject metadata, and bootstrap output.
- Added tests proving beginner docs exist, cross-link, and explain required packet fields and common validator failures.

## 0.2.0 - 2026-05-14

- Added dependency-free repo file inventory builder and query scripts.
- Added repo file index schema and compact JSON summary/query output.
- Added read-only command harness contract, schema, validator, and snapshot-based no-write proof.
- Deepened slice-packet semantic validation for vague goals, chat-only evidence, refresh flag rationale, and write-intent focused commands.
- Wired file-index and read-only harness checks into bootstrap, Makefile validation, generated entrypoints, and pyproject metadata.
- Added low-token file-inventory coverage to the small config-tool example.

## 0.1.0 - 2026-05-14

- Added canonical methodology JSON as the source of doctrine.
- Added generated Markdown entrypoints and renderer drift checks.
- Added dependency-free slice-packet validator.
- Added starter JSON schemas for methodology, slice packets, and refresh decisions.
- Added a generic low-token workflow contract, schema, validator, and bootstrap wiring based on the vbtpro-lab low-token pattern.
- Added minimal and small config-tool examples.
- Added Makefile targets for local checks.
- Added local bootstrap script for seeding new repos from this template.
