#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _governance_ledger import append_closeout_event
from _validator_output import emit_json

REQUIRED = ("implementation_commit", "proof_commands", "residual_classification", "next_slice_ready")


def _closeout_target(root: Path, closeout: Path) -> Path:
    return closeout if closeout.is_absolute() else root / closeout


def _repo_ref(root: Path, target: Path) -> str:
    try:
        return target.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return target.name


def _closeout_entity_id(target: Path, data: dict) -> str:
    for key in ("slice_id", "wave_id", "selected_wave_or_slice", "closeout_id"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    stem = target.stem
    return stem.removesuffix("_closeout") or stem


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("closeout", nargs="?", type=Path)
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--mode", choices=("warning", "strict"), default="strict")
    p.add_argument("--summary-only", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--record-ledger", action="store_true")
    p.add_argument("--ledger-path", type=Path, default=Path("manifests/governance_event_ledger.jsonl"))
    p.add_argument("--timestamp-utc")
    args = p.parse_args(argv)
    root = args.root.resolve()
    targets: list[Path]
    if args.closeout:
        targets = [_closeout_target(root, args.closeout)]
    else:
        targets = sorted((root / "closeouts").glob("*.json"))
    fails: list[str] = []
    loaded: list[tuple[Path, dict]] = []
    for target in targets:
        d = json.loads(target.read_text(encoding="utf-8"))
        loaded.append((target, d))
        rel = _repo_ref(root, target)
        fails.extend([f"CLOSEOUT_MISSING_{k.upper()} path={rel}" for k in REQUIRED if k not in d])
        if d.get("generated_refresh_required") and "generated_refresh_commit" not in d:
            fails.append(f"CLOSEOUT_MISSING_GENERATED_REFRESH_COMMIT path={rel}")
    if fails and args.mode == "strict":
        if args.json:
            emit_json(validator="slice_closeout", status="failed", failure_codes=fails)
        else:
            print("FAIL slice_closeout")
            for f in fails:
                print(f)
        return 1

    ledger_events: list[dict[str, object]] = []
    if args.record_ledger and not fails:
        for target, data in loaded:
            entity_id = _closeout_entity_id(target, data)
            ledger_appended = append_closeout_event(
                root=root,
                closeout_id=entity_id,
                artifact_refs=[target],
                ledger_path=args.ledger_path,
                timestamp_utc=args.timestamp_utc,
                details={"closeout_path": _repo_ref(root, target)},
            )
            ledger_events.append({"entity_id": entity_id, "ledger_appended": ledger_appended})

    if args.json:
        emit_json(validator="slice_closeout", status="warn" if fails else "passed", failure_codes=fails)
    elif args.summary_only:
        print(
            json.dumps(
                {
                    "status": "warn" if fails else "passed",
                    "mode": args.mode,
                    "failure_count": len(fails),
                    "target_count": len(targets),
                    "ledger_appended": any(
                        bool(item["ledger_appended"]) for item in ledger_events
                    ),
                    "ledger_events": ledger_events,
                }
            )
        )
    else:
        suffix = ""
        if args.record_ledger:
            appended_count = sum(1 for item in ledger_events if item["ledger_appended"])
            suffix = f" ledger_events={len(ledger_events)} ledger_appended={appended_count}"
        print(
            f"{'WARN' if fails else 'PASS'} slice_closeout "
            f"mode={args.mode} failures={len(fails)}{suffix}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
