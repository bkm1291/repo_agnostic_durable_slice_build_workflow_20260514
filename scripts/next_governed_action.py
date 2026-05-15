#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

roadmap = Path("plans/repo_roadmap.json")
if not roadmap.exists():
    print("FAIL next_governed_action roadmap_missing")
    raise SystemExit(1)
d = json.loads(roadmap.read_text(encoding="utf-8"))
for w in d.get("waves", []):
    if w.get("status") in {"draft", "implementation_ready", "in_progress"}:
        print(json.dumps({"next_wave": w.get("wave_id"), "status": w.get("status"), "packet": w.get("packet")}))
        raise SystemExit(0)
print(json.dumps({"next_wave": None, "status": "none_ready"}))
