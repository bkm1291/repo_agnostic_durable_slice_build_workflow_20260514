#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ID_RE = re.compile(r"^plan_note_[a-z0-9_]+_[0-9]{8}$")
TS_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")


def validate(root: Path, strict: bool) -> list[str]:
    failures: list[str] = []
    for path in sorted((root / "plans" / "notes").glob("*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            failures.append(f"PLAN_NOTE_JSON_INVALID path={path.relative_to(root).as_posix()}")
            continue
        rel = path.relative_to(root).as_posix()
        if d.get("schema_version") != "v1.plan_note.1":
            failures.append(f"PLAN_NOTE_BAD_SCHEMA path={rel}")
        if not ID_RE.match(str(d.get("plan_note_id", ""))):
            failures.append(f"PLAN_NOTE_BAD_ID path={rel}")
        if not TS_RE.match(str(d.get("created_at", ""))):
            failures.append(f"PLAN_NOTE_BAD_TIMESTAMP path={rel}")
        if strict and d.get("status") not in {"active", "draft", "superseded"}:
            failures.append(f"PLAN_NOTE_BAD_STATUS path={rel}")
    return failures


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--mode", choices=("warning", "strict"), default="strict")
    p.add_argument("--summary-only", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    failures = validate(args.root, strict=args.mode == "strict")
    if failures and args.mode == "strict":
        if args.json:
            print(json.dumps({"status": "failed", "failure_codes": failures, "count": len(failures)}))
        else:
            print("FAIL plan_notes")
            for f in failures:
                print(f)
        return 1
    status = "WARN" if failures else "PASS"
    if args.json:
        print(json.dumps({"status": "warn" if failures else "passed", "failure_codes": failures, "count": len(failures)}))
    else:
        print(f"{status} plan_notes mode={args.mode} failures={len(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
