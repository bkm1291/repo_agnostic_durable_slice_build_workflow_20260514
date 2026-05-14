# Annotated Slice Packet

This page explains every required slice-packet field in beginner language.

The actual packet must be valid JSON. JSON does not allow comments, so keep
annotations in this Markdown file and keep packet files comment-free.

## Minimal Packet

```json
{
  "selected_wave_or_slice": "slice_001",
  "goal": "Render a greeting from validated config-owned runtime values.",
  "files_to_create_or_edit": [
    "configs/greeting_config.json",
    "schemas/greeting_config.schema.json",
    "scripts/validate_greeting_config.py",
    "scripts/render_greeting.py",
    "tests/test_greeting_tool.py"
  ],
  "exact_owner_configs_schemas_contracts": [
    "configs/greeting_config.json",
    "schemas/greeting_config.schema.json"
  ],
  "required_source_reads": [
    {
      "read_id": "methodology_json",
      "surface": "repo-local durable workflow README",
      "read_type": "docs",
      "status": "satisfied",
      "evidence_ref": "source_read:methodology_json"
    }
  ],
  "owning_wave_validator": "scripts/validate_greeting_config.py",
  "owning_wave_tests": [
    "tests/test_greeting_tool.py"
  ],
  "focused_validators_and_tests": [
    "python scripts/validate_greeting_config.py configs/greeting_config.json --summary-only",
    "python scripts/render_greeting.py --config configs/greeting_config.json",
    "python -m pytest -q tests/test_greeting_tool.py"
  ],
  "not_in_scope": [
    "Argument-driven runtime override",
    "Generated config variable inventory implementation",
    "Packaging or installation"
  ],
  "boundary_rules": {
    "allowed_scope": [
      "Greeting config, schema, renderer, validator, and focused tests"
    ],
    "forbidden_path_prefixes": [
      "manifests/",
      "receipts/"
    ],
    "forbidden_keywords": [
      "Packaging or installation"
    ],
    "planned_future_surface_ids": [
      "config_variable_inventory"
    ]
  },
  "refresh_decision": {
    "repo_index_required": false,
    "script_import_index_required": false,
    "plan_note_index_required": false,
    "config_variable_inventory_required": true,
    "output_schema_index_required": false,
    "post_output_hook_required": false,
    "next_wave_discovery_depends_on_new_surfaces": true,
    "required_reason": "the next slice would need fresh discovery of the new config-owned runtime fields",
    "refresh_timing": "after_implementation_commit",
    "decision_basis": [
      "This slice creates a new runtime config and schema.",
      "Future slices should discover config-owned runtime values without reading chat."
    ]
  },
  "commit_plan": {
    "implementation_commit": "config_cli_validator_tests",
    "generated_refresh_commit": "config_inventory_refresh_after_implementation",
    "do_not_chase_head_only_staleness": true
  }
}
```

## Field Guide

### `selected_wave_or_slice`

The slice id from the roadmap.

Use stable ids such as `slice_001`, `wave_02_config_cli`, or `auth_login_slice`.

### `goal`

One concrete sentence describing what will work after the slice.

Good:

```json
"Render a greeting from validated config-owned runtime values."
```

Too vague:

```json
"Improve config stuff."
```

### `files_to_create_or_edit`

Every file this slice is allowed to create or edit.

If implementation needs another file, update the packet before editing it.

### `exact_owner_configs_schemas_contracts`

The durable owner surfaces for behavior and shape.

Use an empty list only for tiny documentation or bootstrap slices that truly do
not have a config, schema, or contract owner.

### `required_source_reads`

The exact local evidence read before implementation.

Use repo files, local docs, schemas, contracts, or indexes. Do not use chat as
evidence.

When the repo has `plans/source_read_register.json`, cite a durable read with
`read_id` and `evidence_ref: "source_read:<read_id>"`. Use `full_source` or
`full_read` when exact implementation behavior depends on a source/API surface,
and use `docs` for normal local documentation.

### `owning_wave_validator`

The main validator for the slice.

This should be a script that can fail with useful messages.

### `owning_wave_tests`

The focused test files that prove this slice.

### `focused_validators_and_tests`

The commands to run before closeout.

Keep these mostly read-only. Writer or generator commands belong in explicit
implementation or generated-refresh steps.

### `not_in_scope`

Things you are deliberately not building in this slice.

This protects beginners from turning a small slice into an open-ended project.

### `boundary_rules`

Machine-checkable scope guards for this slice.

- `allowed_scope`: what this slice may change.
- `forbidden_path_prefixes`: path families this slice must not edit.
- `forbidden_keywords`: scope topics that must stay in `not_in_scope`.
- `planned_future_surface_ids`: future registry ids that are intentionally not
  implemented in this slice.

Use `plans/planned_future_surfaces.json` to make intentionally absent future
files visible without treating them as broken current work.

### `refresh_decision`

Whether generated discovery needs to refresh after implementation.

Most first slices can use all `false` flags and `refresh_timing: "skip"`.

Set a flag to `true` only when future work needs fresh generated discovery.

### `commit_plan`

How the work should be committed.

Use one implementation commit first. If generated refresh is required, use a
second commit for generated outputs.
