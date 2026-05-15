from __future__ import annotations

import json


def emit_json(*, validator: str, status: str, failure_codes: list[str], warnings: list[str] | None = None) -> None:
    payload = {
        "validator": validator,
        "status": status,
        "failure_codes": failure_codes,
        "warnings": warnings or [],
        "count": len(failure_codes),
    }
    print(json.dumps(payload))
