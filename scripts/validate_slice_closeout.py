#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = ("implementation_commit", "proof_commands", "residual_classification", "next_slice_ready")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("closeout", type=Path)
    p.add_argument("--mode", choices=("warning", "strict"), default="strict")
    args = p.parse_args(argv)
    d = json.loads(args.closeout.read_text(encoding="utf-8"))
    fails = [f"CLOSEOUT_MISSING_{k.upper()}" for k in REQUIRED if k not in d]
    if d.get("generated_refresh_required") and "generated_refresh_commit" not in d:
        fails.append("CLOSEOUT_MISSING_GENERATED_REFRESH_COMMIT")
    if fails and args.mode == "strict":
        print("FAIL slice_closeout")
        for f in fails:
            print(f)
        return 1
    print(f"{'WARN' if fails else 'PASS'} slice_closeout mode={args.mode} failures={len(fails)}")
    return 0
