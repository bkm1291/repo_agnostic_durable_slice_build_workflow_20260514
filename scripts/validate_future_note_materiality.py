#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

MATERIAL_KEYS = {
    "execution_strategy",
    "slices",
    "commit_shape",
    "validation_matrix",
    "risk_controls",
    "priorities",
}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--mode", choices=("warning", "strict"), default="strict")
    args = p.parse_args(argv)
    fails: list[str] = []
    for path in sorted((args.root / "plans" / "notes").glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        if not MATERIAL_KEYS.intersection(d.keys()):
            fails.append(f"FUTURE_NOTE_NOT_MATERIAL path={path.relative_to(args.root).as_posix()}")
    if fails and args.mode == "strict":
        print("FAIL future_note_materiality")
        for f in fails:
            print(f)
        return 1
    print(f"{'WARN' if fails else 'PASS'} future_note_materiality mode={args.mode} failures={len(fails)}")
    return 0
