#!/usr/bin/env python3
"""Build or check a compact repo file inventory using only the standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


DEFAULT_OUTPUT = Path("manifests/repo_file_index.json")
EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}
TEXT_EXTENSIONS = {
    ".cfg",
    ".css",
    ".csv",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def _repo_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _is_safe_relpath(value: str) -> bool:
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def _git_inventory(root: Path) -> tuple[str, list[Path]] | None:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    files: list[Path] = []
    for line in result.stdout.splitlines():
        rel = line.strip()
        if rel and _is_safe_relpath(rel):
            files.append(root / rel)
    return "git_ls_files_cached_and_untracked", files


def _filesystem_inventory(root: Path) -> tuple[str, list[Path]]:
    files = [
        item
        for item in root.rglob("*")
        if item.is_file() and not any(part in EXCLUDED_DIRS for part in item.relative_to(root).parts)
    ]
    return "filesystem_walk", files


def _iter_inventory(root: Path) -> tuple[str, list[Path]]:
    return _git_inventory(root) or _filesystem_inventory(root)


def _classify_path(relpath: str) -> str:
    path = PurePosixPath(relpath)
    parts = path.parts
    suffix = path.suffix.lower()
    if parts[0] == "tests" or "/tests/" in f"/{relpath}/" or path.name.startswith("test_"):
        return "test"
    if parts[0] == "schemas" or suffix == ".schema.json":
        return "schema"
    if parts[0] == "contracts":
        return "contract"
    if parts[0] == "configs":
        return "config"
    if parts[0] == "plans":
        return "plan"
    if parts[0] in {"manifests", "reports", "receipts"}:
        return "generated_or_evidence"
    if parts[0] == "scripts" or suffix in {".py", ".sh"}:
        return "script"
    if suffix in {".md", ".rst", ".txt"} or path.name in {"README", "LICENSE"}:
        return "doc"
    return "source"


def _text_line_count(data: bytes, suffix: str) -> int | None:
    if suffix.lower() not in TEXT_EXTENSIONS and b"\0" in data[:2048]:
        return None
    try:
        return len(data.decode("utf-8").splitlines())
    except UnicodeDecodeError:
        return None


def _file_entry(path: Path, root: Path) -> dict[str, Any]:
    relpath = _repo_relative(path, root)
    data = path.read_bytes()
    suffix = path.suffix.lower()
    line_count = _text_line_count(data, suffix)
    return {
        "path": relpath,
        "kind": _classify_path(relpath),
        "extension": suffix,
        "size_bytes": len(data),
        "line_count": line_count,
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def build_index(root: Path, output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    root = root.resolve()
    output_abs = (root / output_path).resolve() if not output_path.is_absolute() else output_path.resolve()
    inventory_mode, files = _iter_inventory(root)
    entries = []
    for file_path in sorted({path.resolve() for path in files}):
        if not file_path.exists() or not file_path.is_file():
            continue
        if file_path == output_abs:
            continue
        rel_parts = file_path.relative_to(root).parts
        if any(part in EXCLUDED_DIRS for part in rel_parts):
            continue
        entries.append(_file_entry(file_path, root))
    kind_counts = Counter(entry["kind"] for entry in entries)
    return {
        "schema_version": "v1.repo_file_index.1",
        "index_id": "repo_file_index",
        "inventory_mode": inventory_mode,
        "root_name": root.name,
        "summary": {
            "file_count": len(entries),
            "kind_counts": dict(sorted(kind_counts.items())),
        },
        "files": entries,
    }


def _stable_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _summary_payload(index: dict[str, Any], *, status: str, output_path: Path) -> dict[str, Any]:
    return {
        "status": status,
        "index_id": index.get("index_id"),
        "inventory_mode": index.get("inventory_mode"),
        "file_count": index.get("summary", {}).get("file_count"),
        "kind_counts": index.get("summary", {}).get("kind_counts", {}),
        "output_path": output_path.as_posix(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Write the generated index")
    mode.add_argument("--check", action="store_true", help="Fail if the output index is missing or stale")
    parser.add_argument("--summary-only", action="store_true", help="Print compact JSON")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    output_path = args.output
    output_abs = output_path if output_path.is_absolute() else root / output_path
    index = build_index(root, output_path)
    expected = _stable_json(index)

    if args.write:
        output_abs.parent.mkdir(parents=True, exist_ok=True)
        output_abs.write_text(expected, encoding="utf-8")
        print(json.dumps(_summary_payload(index, status="passed", output_path=output_path)))
        return 0

    if args.check:
        if not output_abs.exists():
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "failure": "REPO_FILE_INDEX_MISSING",
                        "output_path": output_path.as_posix(),
                    }
                )
            )
            return 1
        current = output_abs.read_text(encoding="utf-8")
        if current != expected:
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "failure": "REPO_FILE_INDEX_STALE",
                        "output_path": output_path.as_posix(),
                    }
                )
            )
            return 1
        print(json.dumps(_summary_payload(index, status="passed", output_path=output_path)))
        return 0

    if args.summary_only:
        print(json.dumps(_summary_payload(index, status="passed", output_path=output_path)))
    else:
        print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
