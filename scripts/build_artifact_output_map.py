#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _governance_ledger import append_generated_refresh_event


def build_map() -> dict:
    return {
        "schema_version": "v1.artifact_output_map.1",
        "map_id": "artifact_output_map",
        "outputs": [
            {
                "writer_command_id": "write_repo_file_index",
                "output_path": "manifests/repo_file_index.json",
                "artifact_kind": "generated_index",
                "role": "evidence",
                "summary_only": False,
            },
            {
                "writer_command_id": "write_command_map",
                "output_path": "manifests/command_map.json",
                "artifact_kind": "generated_index",
                "role": "evidence",
                "summary_only": False,
            },
            {
                "writer_command_id": "write_plan_note_index",
                "output_path": "manifests/plan_note_index.json",
                "artifact_kind": "generated_index",
                "role": "authority",
                "summary_only": False,
            },
            {
                "writer_command_id": "write_artifact_output_map",
                "output_path": "manifests/artifact_output_map.json",
                "artifact_kind": "generated_index",
                "role": "authority",
                "summary_only": False,
            },
            {
                "writer_command_id": "record_slice_closeout",
                "output_path": "manifests/governance_event_ledger.jsonl",
                "artifact_kind": "manifest",
                "role": "evidence",
                "summary_only": False,
            },
            {
                "writer_command_id": "record_release_gate",
                "output_path": "manifests/governance_event_ledger.jsonl",
                "artifact_kind": "manifest",
                "role": "evidence",
                "summary_only": False,
            },
        ],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--output", type=Path, default=Path("manifests/artifact_output_map.json"))
    p.add_argument("--write", action="store_true")
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args(argv)
    data = build_map()
    ledger_appended = False
    if args.write:
        out = args.root / args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        ledger_appended = append_generated_refresh_event(
            root=args.root,
            writer_command_id="write_artifact_output_map",
            artifact_refs=[out],
            validator_ref="scripts/build_artifact_output_map.py",
        )
    print(json.dumps({"status": "passed", "output_count": len(data["outputs"]), "ledger_appended": ledger_appended} if args.summary_only else data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
