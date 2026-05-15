#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from _validator_output import emit_json

TS_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
PLAN_RE = re.compile(r"^plan_note_[a-z0-9_]+_[0-9]{8}$")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--mode", choices=("warning", "strict"), default="strict")
    p.add_argument("--summary-only", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    fails: list[str] = []
    for path in sorted((args.root / "plans" / "notes").glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        rel = path.relative_to(args.root).as_posix()
        if not PLAN_RE.match(str(d.get("plan_note_id", ""))):
            fails.append(f"BAD_PLAN_NOTE_ID path={rel}")
        if not TS_RE.match(str(d.get("created_at", ""))):
            fails.append(f"BAD_CREATED_AT path={rel}")
    if fails and args.mode == "strict":
        if args.json:
            emit_json(validator="governance_ids_timestamps", status="failed", failure_codes=fails)
        else:
            print("FAIL governance_ids_timestamps")
            for f in fails:
                print(f)
        return 1
    if args.json:
        emit_json(
            validator="governance_ids_timestamps",
            status="warn" if fails else "passed",
            failure_codes=fails,
        )
    else:
        print(f"{'WARN' if fails else 'PASS'} governance_ids_timestamps mode={args.mode} failures={len(fails)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
