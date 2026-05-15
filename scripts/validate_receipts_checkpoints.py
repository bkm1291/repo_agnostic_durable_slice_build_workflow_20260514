#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REASON = {"writer", "generator", "materializer", "external_action", "irreversible_decision", "closeout_gate"}


def _check(path: Path) -> list[str]:
    d = json.loads(path.read_text(encoding="utf-8"))
    fails: list[str] = []
    if d.get("reason_class") not in REASON:
        fails.append("BAD_REASON_CLASS")
    if "status" in d and len(d.keys()) <= 3:
        fails.append("STATUS_ONLY_RECORD")
    for k in ("related_command", "artifacts_proven", "validation_refs"):
        if k not in d:
            fails.append(f"MISSING_{k.upper()}")
    return fails


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    failures: list[str] = []
    for folder in ("receipts", "checkpoints"):
        base = args.root / folder
        if not base.exists():
            continue
        for path in base.rglob("*.json"):
            for f in _check(path):
                failures.append(f"{f} path={path.relative_to(args.root).as_posix()}")
    if failures:
        print("FAIL receipts_checkpoints")
        for f in failures:
            print(f)
        return 1
    print("PASS receipts_checkpoints" if args.summary_only else "ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
