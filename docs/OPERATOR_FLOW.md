# Operator Flow

Use this loop for each governed slice:

1. Create or update the slice packet with `python scripts/new_slice_packet.py`.
2. Validate the packet with `python scripts/validate_slice_packet.py <packet> --summary-only`.
3. Implement only the owner bundle named in the packet.
4. Validate closeout evidence with `python scripts/validate_slice_closeout.py --mode strict`.
5. Run `make governance-check`.
6. Run `python scripts/validate_release_package.py --json` before release or template handoff.

Generated refreshes, closeouts, release gates, and external actions must be represented in `manifests/governance_event_ledger.jsonl` when they become durable workflow evidence. Explicit manifest writer commands append generated-refresh ledger events automatically and skip duplicate event IDs on repeated runs.
