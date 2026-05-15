#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import json
import re
from pathlib import Path

PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}"),
    re.compile(r"https?://[^/\s:@]+:[^/\s:@]+@"),
]
PREFIX_PATTERNS = [re.compile(r"\b(sk-[A-Za-z0-9]{12,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})\b")]


def _entropy(s: str) -> float:
    if not s:
        return 0.0
    probs = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in probs)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--policy", type=Path, default=Path("configs/no_secrets_persisted_policy.json"))
    p.add_argument("--summary-only", action="store_true")
    p.add_argument("--mode", choices=("warning", "strict"), default="strict")
    args = p.parse_args(argv)
    policy = json.loads((args.root / args.policy).read_text(encoding="utf-8"))
    allow = [re.compile(x) for x in policy.get("allowlist_patterns", [])]
    failures: list[str] = []
    warnings: list[str] = []
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
                    failures.append(f"SECRET_LIKE severity=high path={path.relative_to(args.root).as_posix()}")
                    break
            for pat in PREFIX_PATTERNS:
                if pat.search(text):
                    failures.append(f"SECRET_PREFIX severity=high path={path.relative_to(args.root).as_posix()}")
            for word in re.findall(r"[A-Za-z0-9_\-]{24,}", text):
                has_alpha = any(c.isalpha() for c in word)
                has_digit = any(c.isdigit() for c in word)
                has_sep = any(c in "_-" for c in word)
                vowel_ratio = sum(c.lower() in "aeiou" for c in word) / len(word)
                looks_keyish = has_alpha and has_digit and (has_sep or vowel_ratio < 0.25)
                if looks_keyish and _entropy(word) >= 4.2 and not any(a.search(word) for a in allow):
                    warnings.append(f"HIGH_ENTROPY_TOKEN severity=medium path={path.relative_to(args.root).as_posix()}")
                    break
    if failures and args.mode == "strict":
        print("FAIL no_secrets_persisted")
        for f in failures[:20]:
            print(f)
        return 1
    total_warn = len(warnings)
    status = "WARN" if (failures or warnings) else "PASS"
    print(f"{status} no_secrets_persisted mode={args.mode} failures={len(failures)} warnings={total_warn}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
