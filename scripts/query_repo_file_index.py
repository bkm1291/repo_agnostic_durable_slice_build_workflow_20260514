#!/usr/bin/env python3
"""Query a repo file inventory without reading broad repo surfaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_INDEX = Path("manifests/repo_file_index.json")


def _load_index(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("repo file index must be a JSON object")
    return payload


def _matches(entry: dict[str, Any], args: argparse.Namespace) -> bool:
    path = str(entry.get("path", ""))
    if args.path_contains and args.path_contains not in path:
        return False
    if args.kind and entry.get("kind") != args.kind:
        return False
    if args.extension and entry.get("extension") != args.extension:
        return False
    if args.max_size_bytes is not None:
        size = entry.get("size_bytes")
        if not isinstance(size, int) or size > args.max_size_bytes:
            return False
    return True


def query_index(index: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    files = index.get("files", [])
    if not isinstance(files, list):
        raise ValueError("repo file index files must be a list")
    matches = [
        {
            "path": entry.get("path"),
            "kind": entry.get("kind"),
            "extension": entry.get("extension"),
            "line_count": entry.get("line_count"),
            "size_bytes": entry.get("size_bytes"),
        }
        for entry in files
        if isinstance(entry, dict) and _matches(entry, args)
    ]
    limited = matches[: args.limit]
    return {
        "status": "passed",
        "index_id": index.get("index_id"),
        "match_count": len(matches),
        "returned_count": len(limited),
        "matches": limited,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--path-contains")
    parser.add_argument("--kind")
    parser.add_argument("--extension")
    parser.add_argument("--max-size-bytes", type=int)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--summary-only", action="store_true", help="Print compact JSON")
    args = parser.parse_args(argv)

    try:
        index = _load_index(args.index)
        result = query_index(index, args)
    except FileNotFoundError:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "failure": "REPO_FILE_INDEX_MISSING",
                    "index_path": args.index.as_posix(),
                }
            )
        )
        return 1
    except (json.JSONDecodeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "failure": "REPO_FILE_INDEX_INVALID",
                    "detail": str(exc),
                    "index_path": args.index.as_posix(),
                }
            )
        )
        return 1

    if args.summary_only:
        print(json.dumps(result))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
