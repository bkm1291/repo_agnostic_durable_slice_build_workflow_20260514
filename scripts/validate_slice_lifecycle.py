#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ORDER = ["draft", "implementation_ready", "in_progress", "closed"]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--roadmap", type=Path, default=Path("plans/repo_roadmap.json"))
    p.add_argument("--mode", choices=("warning", "strict"), default="strict")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if not args.roadmap.exists():
        if args.json:
            print(json.dumps({"status": "warn", "failure_codes": ["ROADMAP_MISSING"], "count": 1}))
        else:
            print("WARN slice_lifecycle mode=strict failures=1")
            print("ROADMAP_MISSING")
        return 0
    d = json.loads(args.roadmap.read_text(encoding="utf-8"))
    fails: list[str] = []
    for w in d.get("waves", []):
        if w.get("status") not in ORDER:
            fails.append(f"LIFECYCLE_BAD_STATUS wave={w.get('wave_id')}")
        for dep in w.get("depends_on", []):
            if dep not in {x.get("wave_id") for x in d.get("waves", [])}:
                fails.append(f"ORPHAN_DEPENDENCY wave={w.get('wave_id')} depends_on={dep}")
    if fails and args.mode == "strict":
        if args.json:
            print(json.dumps({"status": "failed", "failure_codes": fails, "count": len(fails)}))
        else:
            print("FAIL slice_lifecycle")
            for f in fails:
                print(f)
        return 1
    if args.json:
        print(json.dumps({"status": "warn" if fails else "passed", "failure_codes": fails, "count": len(fails)}))
    else:
        print(f"{'WARN' if fails else 'PASS'} slice_lifecycle mode={args.mode} failures={len(fails)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
