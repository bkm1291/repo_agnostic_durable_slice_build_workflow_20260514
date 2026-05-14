#!/usr/bin/env python3
"""Render a greeting from config-owned runtime values."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def render_greeting(config_path: Path) -> str:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    return f"{config['message']}, {config['recipient']}{config['punctuation']}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    print(render_greeting(args.config))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
