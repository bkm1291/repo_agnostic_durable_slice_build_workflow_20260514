#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--mode", choices=("warning", "strict"), default="strict")
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    root = args.root
    failures: list[str] = []

    planned = json.loads((root / "plans/planned_future_surfaces.json").read_text(encoding="utf-8"))
    for s in planned.get("surfaces", []):
        path = root / s["path"]
        status = s.get("status")
        if status == "planned_not_created" and path.exists():
            failures.append(f"PLANNED_SURFACE_EXISTS path={s['path']}")
        if status == "active" and not path.exists():
            failures.append(f"ACTIVE_SURFACE_MISSING path={s['path']}")

    cmd_map = json.loads((root / "manifests/command_map.json").read_text(encoding="utf-8")) if (root / "manifests/command_map.json").exists() else {"commands": []}
    art_map = json.loads((root / "manifests/artifact_output_map.json").read_text(encoding="utf-8"))
    writer_ids = {c["command_id"] for c in cmd_map.get("commands", []) if c.get("side_effect_class") == "write_explicit"}
    for out in art_map.get("outputs", []):
        if out["writer_command_id"] not in writer_ids and args.mode == "strict":
            failures.append(f"ARTIFACT_WRITER_NOT_IN_COMMAND_MAP writer={out['writer_command_id']}")

    repo_idx = json.loads((root / "manifests/repo_file_index.json").read_text(encoding="utf-8")) if (root / "manifests/repo_file_index.json").exists() else {"files": []}
    kind_by_path = {f["path"]: f["kind"] for f in repo_idx.get("files", [])}
    for out in art_map.get("outputs", []):
        pth = out["output_path"]
        if pth in kind_by_path and not kind_by_path[pth].startswith("artifact:"):
            failures.append(f"REPO_INDEX_KIND_MISMATCH path={pth} kind={kind_by_path[pth]}")

    if failures and args.mode == "strict":
        print("FAIL cross_surface_consistency")
        for f in failures:
            print(f)
        return 1
    print(f"{'WARN' if failures else 'PASS'} cross_surface_consistency mode={args.mode} failures={len(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
