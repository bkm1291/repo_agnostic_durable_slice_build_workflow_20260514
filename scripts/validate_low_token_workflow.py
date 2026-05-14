#!/usr/bin/env python3
"""Validate the generic low-token workflow contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_CONTRACT = Path("contracts/low_token_workflow_contract.json")
REQUIRED_TOP_LEVEL_FIELDS = (
    "schema_version",
    "contract_id",
    "status",
    "purpose",
    "default_limits",
    "bootstrap_exception",
    "forbidden_full_reads",
    "preferred_routing_surfaces",
    "mandatory_sequence",
    "read_escalation_ladder",
    "command_output_policy",
    "slice_packet_integration",
    "supporting_tools",
    "repo_gate_enforcement",
)
REQUIRED_LIMITS = (
    "max_targeted_read_lines",
    "max_tool_output_tokens_default",
    "max_sync_calls_per_doc_slice",
    "max_validate_only_calls_per_doc_slice",
    "raw_sync_output_allowed",
    "raw_validate_only_output_allowed",
)
REQUIRED_LADDER_TIERS = (
    "tier_0",
    "tier_1",
    "tier_2",
    "tier_3",
    "tier_4",
    "required_escalation_phrase",
)
REQUIRED_SEQUENCE_STEPS = (
    "query_or_file_inventory_first",
    "targeted_read_only",
    "focused_parse_or_validator",
    "stop",
)


def _load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"LOW_TOKEN_CONTRACT_MISSING path={path}"]
    except json.JSONDecodeError as exc:
        return None, [f"LOW_TOKEN_CONTRACT_JSON_INVALID line={exc.lineno} column={exc.colno}"]


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_contract(contract: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(contract, dict):
        return ["LOW_TOKEN_CONTRACT_NOT_OBJECT"]

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in contract:
            failures.append(f"LOW_TOKEN_MISSING_FIELD field={field}")

    limits = contract.get("default_limits")
    if not isinstance(limits, dict):
        failures.append("LOW_TOKEN_DEFAULT_LIMITS_NOT_OBJECT")
    else:
        for field in REQUIRED_LIMITS:
            if field not in limits:
                failures.append(f"LOW_TOKEN_LIMIT_MISSING field={field}")
        if isinstance(limits.get("max_targeted_read_lines"), int) and limits["max_targeted_read_lines"] > 120:
            failures.append("LOW_TOKEN_TARGETED_READ_LIMIT_TOO_HIGH")
        if isinstance(limits.get("max_tool_output_tokens_default"), int) and limits["max_tool_output_tokens_default"] > 4000:
            failures.append("LOW_TOKEN_OUTPUT_TOKEN_LIMIT_TOO_HIGH")
        if limits.get("raw_sync_output_allowed") is not False:
            failures.append("LOW_TOKEN_RAW_SYNC_OUTPUT_NOT_DISABLED")
        if limits.get("raw_validate_only_output_allowed") is not False:
            failures.append("LOW_TOKEN_RAW_VALIDATE_OUTPUT_NOT_DISABLED")

    forbidden = contract.get("forbidden_full_reads")
    if not isinstance(forbidden, list) or not forbidden:
        failures.append("LOW_TOKEN_FORBIDDEN_FULL_READS_EMPTY")
    elif not any("JSONL" in str(item).upper() or "LOG" in str(item).upper() for item in forbidden):
        failures.append("LOW_TOKEN_FORBIDDEN_FULL_READS_MISSING_LOG_OR_JSONL")

    sequence = contract.get("mandatory_sequence")
    if not isinstance(sequence, dict):
        failures.append("LOW_TOKEN_SEQUENCE_NOT_OBJECT")
    else:
        doc_sequence = sequence.get("doc_or_plan_only_slice")
        if not isinstance(doc_sequence, list) or not doc_sequence:
            failures.append("LOW_TOKEN_DOC_SEQUENCE_EMPTY")
        else:
            for step in REQUIRED_SEQUENCE_STEPS:
                if step not in doc_sequence:
                    failures.append(f"LOW_TOKEN_DOC_SEQUENCE_MISSING_STEP step={step}")

    ladder = contract.get("read_escalation_ladder")
    if not isinstance(ladder, dict):
        failures.append("LOW_TOKEN_READ_LADDER_NOT_OBJECT")
    else:
        for tier in REQUIRED_LADDER_TIERS:
            if tier not in ladder:
                failures.append(f"LOW_TOKEN_READ_LADDER_MISSING field={tier}")
        phrase = ladder.get("required_escalation_phrase")
        if not _is_nonempty_string(phrase):
            failures.append("LOW_TOKEN_ESCALATION_PHRASE_EMPTY")
        elif not all(token in phrase for token in ("<specific missing fact>", "<path>", "<range>")):
            failures.append("LOW_TOKEN_ESCALATION_PHRASE_MISSING_PLACEHOLDERS")

    output_policy = contract.get("command_output_policy")
    if not isinstance(output_policy, dict):
        failures.append("LOW_TOKEN_OUTPUT_POLICY_NOT_OBJECT")
    else:
        if output_policy.get("command_stdout_default") != "compact_json_summary_only":
            failures.append("LOW_TOKEN_STDOUT_DEFAULT_NOT_COMPACT")
        if output_policy.get("summary_only_modes_must_be_read_only") is not True:
            failures.append("LOW_TOKEN_SUMMARY_ONLY_NOT_READ_ONLY")
        if output_policy.get("writer_modes_require_explicit_intent") is not True:
            failures.append("LOW_TOKEN_WRITER_MODES_NOT_EXPLICIT")
        summary_fields = output_policy.get("compact_summary_fields")
        if not isinstance(summary_fields, list) or not summary_fields:
            failures.append("LOW_TOKEN_SUMMARY_FIELDS_EMPTY")

    supporting_tools = contract.get("supporting_tools")
    if not isinstance(supporting_tools, dict):
        failures.append("LOW_TOKEN_SUPPORTING_TOOLS_NOT_OBJECT")
    else:
        expected_tools = {
            "file_inventory_builder": "scripts/build_repo_file_index.py",
            "file_inventory_query": "scripts/query_repo_file_index.py",
            "read_only_command_harness": "scripts/validate_read_only_commands.py",
            "read_only_command_contract": "contracts/read_only_command_harness.json",
        }
        for field, expected in expected_tools.items():
            if supporting_tools.get(field) != expected:
                failures.append(f"LOW_TOKEN_SUPPORTING_TOOL_MISMATCH field={field}")

    enforcement = contract.get("repo_gate_enforcement")
    if isinstance(enforcement, dict):
        if enforcement.get("check_script") != "scripts/validate_low_token_workflow.py":
            failures.append("LOW_TOKEN_ENFORCEMENT_SCRIPT_MISMATCH")
        checks = enforcement.get("required_checks")
        if not isinstance(checks, list) or "required_escalation_phrase_present" not in checks:
            failures.append("LOW_TOKEN_ENFORCEMENT_CHECKS_INCOMPLETE")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "contract",
        nargs="?",
        type=Path,
        default=DEFAULT_CONTRACT,
        help="Path to the low-token workflow contract JSON",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print a compact result and do not write artifacts",
    )
    args = parser.parse_args(argv)

    document, load_failures = _load_json(args.contract)
    failures = load_failures or validate_contract(document)
    if failures:
        print(f"FAIL low_token_workflow path={args.contract} failures={len(failures)}")
        for failure in failures:
            print(failure)
        return 1

    if args.summary_only:
        print(f"PASS low_token_workflow path={args.contract}")
    else:
        print(f"PASS low_token_workflow path={args.contract} mode=check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
