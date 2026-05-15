#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--map", type=Path, default=Path("manifests/artifact_output_map.json"))
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    doc = json.loads(args.map.read_text(encoding="utf-8"))
    failures: list[str] = []
    for item in doc.get("outputs", []):
        writer_command_id = item.get("writer_command_id", "")
        if item.get("summary_only") and writer_command_id.startswith(("write_", "record_")):
            failures.append("ARTIFACT_MAP_SUMMARY_ONLY_WRITER_INVALID")
    if failures:
        print("FAIL artifact_output_map")
        for f in failures:
            print(f)
        return 1
    print("PASS artifact_output_map" if args.summary_only else json.dumps(doc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
