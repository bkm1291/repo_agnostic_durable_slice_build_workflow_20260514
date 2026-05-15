#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from _governance_ledger import append_generated_refresh_event

DEFAULT_OUTPUT = Path("manifests/plan_note_index.json")
DEFAULT_ACTIVE_OUTPUT = Path("manifests/plan_note_active_set.json")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_index(root: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for path in sorted((root / "plans").rglob("*.json")):
        rel = path.relative_to(root).as_posix()
        doc = _load_json(path)
        if not isinstance(doc, dict):
            continue
        status = str(doc.get("status", "unknown"))
        authority_class = "evidence" if rel.startswith("reports/") else "authority"
        supersedes = doc.get("supersedes", [])
        superseded_by = doc.get("superseded_by", [])
        active_eligible = status == "active" and not superseded_by and authority_class == "authority"
        entries.append(
            {
                "path": rel,
                "status": status,
                "authority_class": authority_class,
                "active_eligible": active_eligible,
                "supersedes": supersedes if isinstance(supersedes, list) else [],
                "superseded_by": superseded_by if isinstance(superseded_by, list) else [],
                "current_decision": str(doc.get("goal", doc.get("purpose", ""))),
                "next_action": str(doc.get("next_action", "")),
                "validation_refs": ["scripts/validate_slice_packet.py"],
            }
        )
    return {"schema_version": "v1.plan_note_index.1", "index_id": "plan_note_index", "entries": entries}


def build_active_set(index: dict[str, Any]) -> dict[str, Any]:
    active = [e for e in index["entries"] if e["active_eligible"]]
    return {"schema_version": "v1.plan_note_active_set.1", "active_paths": [e["path"] for e in active], "count": len(active)}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--active-output", type=Path, default=DEFAULT_ACTIVE_OUTPUT)
    p.add_argument("--write", action="store_true")
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    root = args.root.resolve()
    check = subprocess.run(
        [sys.executable, str(root / "scripts" / "validate_plan_notes.py"), "--root", str(root), "--mode", "strict", "--summary-only"],
        check=False,
        text=True,
        capture_output=True,
    )
    if check.returncode != 0:
        print(check.stdout.strip())
        return 1
    index = build_index(root)
    active = build_active_set(index)
    if args.write:
        out = root / args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
        active_out = root / args.active_output
        active_out.parent.mkdir(parents=True, exist_ok=True)
        active_out.write_text(json.dumps(active, indent=2) + "\n", encoding="utf-8")
        ledger_appended = append_generated_refresh_event(
            root=root,
            writer_command_id="write_plan_note_index",
            artifact_refs=[out, active_out],
            validator_ref="scripts/build_plan_note_index.py",
        )
    else:
        ledger_appended = False
    if args.summary_only:
        print(json.dumps({"status": "passed", "entry_count": len(index["entries"]), "active_count": active["count"], "ledger_appended": ledger_appended}))
    else:
        print(json.dumps(index, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
