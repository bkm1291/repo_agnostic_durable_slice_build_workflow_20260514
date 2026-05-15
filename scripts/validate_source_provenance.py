#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED = Path("docs/SOURCE_PROVENANCE_POLICY.md")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    args = p.parse_args(argv)
    path = args.root / REQUIRED
    if not path.exists():
        print("FAIL source_provenance_policy_missing")
        return 1
    print("PASS source_provenance")
    return 0
