#!/usr/bin/env python3
"""Validate the example greeting config without external dependencies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "greeting_config.schema.json"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_config(config: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field in schema["required_fields"]:
        if field not in config:
            failures.append(f"GREETING_CONFIG_MISSING_FIELD field={field}")

    if config.get("schema_id") != schema["schema_id"]:
        failures.append("GREETING_CONFIG_SCHEMA_ID_MISMATCH")

    for field, limit in (
        ("message", schema["max_message_length"]),
        ("recipient", schema["max_recipient_length"]),
    ):
        value = config.get(field)
        if not isinstance(value, str) or not value.strip():
            failures.append(f"GREETING_CONFIG_TEXT_EMPTY field={field}")
        elif len(value) > limit:
            failures.append(f"GREETING_CONFIG_TEXT_TOO_LONG field={field}")

    if config.get("punctuation") not in schema["allowed_punctuation"]:
        failures.append("GREETING_CONFIG_BAD_PUNCTUATION")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()

    config = _load_json(args.config)
    schema = _load_json(SCHEMA_PATH)
    failures = validate_config(config, schema)
    if failures:
        print(f"FAIL greeting_config path={args.config} failures={len(failures)}")
        for failure in failures:
            print(failure)
        return 1
    print(f"PASS greeting_config path={args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
