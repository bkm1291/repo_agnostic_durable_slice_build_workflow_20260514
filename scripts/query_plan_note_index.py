#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--index", type=Path, default=Path("manifests/plan_note_index.json"))
    p.add_argument("--active-only", action="store_true")
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    data = json.loads(args.index.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    if args.active_only:
        entries = [e for e in entries if e.get("active_eligible")]
    payload = {"match_count": len(entries), "matches": entries}
    print(json.dumps(payload if args.summary_only else entries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
