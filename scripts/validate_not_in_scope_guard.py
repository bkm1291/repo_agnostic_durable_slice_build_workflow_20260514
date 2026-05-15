#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("packet", type=Path)
    p.add_argument("--mode", choices=("warning", "strict"), default="strict")
    args = p.parse_args(argv)
    d = json.loads(args.packet.read_text(encoding="utf-8"))
    items = d.get("not_in_scope", [])
    fails: list[str] = []
    if not isinstance(items, list) or not items:
        fails.append("NOT_IN_SCOPE_EMPTY")
    files = [str(x) for x in d.get("files_to_create_or_edit", [])]
    for token in items:
        t = str(token).lower()
        if any(t and t in f.lower() for f in files):
            fails.append("NOT_IN_SCOPE_CONFLICTS_WITH_EDIT_LIST")
            break
    if fails and args.mode == "strict":
        print("FAIL not_in_scope_guard")
        for f in fails:
            print(f)
        return 1
    print(f"{'WARN' if fails else 'PASS'} not_in_scope_guard mode={args.mode} failures={len(fails)}")
    return 0
