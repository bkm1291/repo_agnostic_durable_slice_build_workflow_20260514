#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED = ("manifests", "receipts", "checkpoints", "reports")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    missing = [d for d in REQUIRED if not (args.root / d).is_dir()]
    if missing:
        print(f"FAIL runtime_governance_dirs missing={','.join(missing)}")
        return 1
    print("PASS runtime_governance_dirs" if args.summary_only else "ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
