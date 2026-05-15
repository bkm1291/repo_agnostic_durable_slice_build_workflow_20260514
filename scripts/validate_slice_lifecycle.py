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
    args = p.parse_args(argv)
    d = json.loads(args.roadmap.read_text(encoding="utf-8"))
    fails: list[str] = []
    for w in d.get("waves", []):
        if w.get("status") not in ORDER:
            fails.append(f"LIFECYCLE_BAD_STATUS wave={w.get('wave_id')}")
        for dep in w.get("depends_on", []):
            if dep not in {x.get("wave_id") for x in d.get("waves", [])}:
                fails.append(f"ORPHAN_DEPENDENCY wave={w.get('wave_id')} depends_on={dep}")
    if fails and args.mode == "strict":
        print("FAIL slice_lifecycle")
        for f in fails:
            print(f)
        return 1
    print(f"{'WARN' if fails else 'PASS'} slice_lifecycle mode={args.mode} failures={len(fails)}")
    return 0
