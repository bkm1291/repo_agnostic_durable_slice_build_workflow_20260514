# Small Config Tool Example

This example is a realistic but small repo shape: a CLI renders a greeting from
config-owned runtime values. The slice packet names the config, schema, runtime
script, validator, focused tests, and a non-skip generated-refresh decision.

Run from this directory:

```bash
python scripts/validate_greeting_config.py configs/greeting_config.json --summary-only
python scripts/render_greeting.py --config configs/greeting_config.json
python ../../scripts/build_repo_file_index.py --root . --summary-only
python ../../scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --planned-future-surfaces ../../plans/planned_future_surfaces.json --summary-only
python -m pytest -q tests
```

This is intentionally tiny, but it demonstrates the workflow transition from
packet -> owner files -> validator -> focused tests -> refresh decision.

The file-index command is the low-token read-routing example: inspect the
inventory first, then open only the exact config, schema, script, or test file
needed for the current slice.
