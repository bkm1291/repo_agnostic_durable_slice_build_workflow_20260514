# Minimal Durable Slice Example

This directory shows the smallest useful version of the workflow.

It contains:

- `plans/repo_roadmap.json`: one durable roadmap
- `plans/slices/slice_001_packet.json`: one implementation packet
- `scripts/validate_slice_packet.py`: one validator
- `tests/test_validate_slice_packet.py`: one focused test file

From this directory, run:

```bash
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
python -m pytest -q tests
```

The example intentionally skips generated index refresh. The slice is proven by
the packet validator and focused tests.
