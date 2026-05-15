#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}"),
    re.compile(r"https?://[^/\s:@]+:[^/\s:@]+@"),
]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--policy", type=Path, default=Path("configs/no_secrets_persisted_policy.json"))
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    policy = json.loads((args.root / args.policy).read_text(encoding="utf-8"))
    allow = [re.compile(x) for x in policy.get("allowlist_patterns", [])]
    failures: list[str] = []
    for rel in policy.get("scan_roots", []):
        base = args.root / rel
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pat in PATTERNS:
                for m in pat.finditer(text):
                    token = m.group(0)
                    if any(a.search(token) for a in allow):
                        continue
                    failures.append(f"SECRET_LIKE path={path.relative_to(args.root).as_posix()}")
                    break
    if failures:
        print("FAIL no_secrets_persisted")
        for f in failures[:20]:
            print(f)
        return 1
    print("PASS no_secrets_persisted" if args.summary_only else "ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
