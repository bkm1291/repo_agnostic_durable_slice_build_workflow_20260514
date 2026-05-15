#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--roadmap", type=Path, default=Path("plans/repo_roadmap.json"))
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--slice-id", required=True)
    args = p.parse_args(argv)
    d = json.loads(args.roadmap.read_text(encoding="utf-8"))
    wave = next((w for w in d.get("waves", []) if w.get("wave_id") == args.slice_id), None)
    if wave is None:
        print("FAIL new_slice_packet wave_not_found")
        return 1
    packet = {"selected_wave_or_slice": args.slice_id, "goal": wave.get("goal", ""), "status": "draft"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(f"PASS new_slice_packet output={args.output.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
