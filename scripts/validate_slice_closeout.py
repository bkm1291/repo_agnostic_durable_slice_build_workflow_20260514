#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = ("implementation_commit", "proof_commands", "residual_classification", "next_slice_ready")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("closeout", nargs="?", type=Path)
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--mode", choices=("warning", "strict"), default="strict")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    targets: list[Path]
    if args.closeout:
        targets = [args.closeout]
    else:
        targets = sorted((args.root / "closeouts").glob("*.json"))
    fails: list[str] = []
    for target in targets:
        d = json.loads(target.read_text(encoding="utf-8"))
        rel = target.relative_to(args.root).as_posix() if target.is_absolute() else target.as_posix()
        fails.extend([f"CLOSEOUT_MISSING_{k.upper()} path={rel}" for k in REQUIRED if k not in d])
        if d.get("generated_refresh_required") and "generated_refresh_commit" not in d:
            fails.append(f"CLOSEOUT_MISSING_GENERATED_REFRESH_COMMIT path={rel}")
    if fails and args.mode == "strict":
        if args.json:
            print(json.dumps({"status": "failed", "failure_codes": fails}))
        else:
            print("FAIL slice_closeout")
            for f in fails:
                print(f)
        return 1
    if args.json:
        print(json.dumps({"status": "warn" if fails else "passed", "failure_codes": fails, "count": len(fails)}))
    else:
        print(f"{'WARN' if fails else 'PASS'} slice_closeout mode={args.mode} failures={len(fails)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
