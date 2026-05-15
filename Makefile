PYTHON ?= python

.PHONY: check governance-check render render-check test validate-examples clean bootstrap-smoke release-check repo-index repo-index-check read-only-check

check: render-check validate-examples test release-check

governance-check:
	$(PYTHON) scripts/validate_plan_notes.py --summary-only
	$(PYTHON) scripts/build_command_map.py --write --summary-only
	$(PYTHON) scripts/build_repo_file_index.py --write --summary-only
	$(PYTHON) scripts/build_plan_note_index.py --summary-only
	$(PYTHON) scripts/build_artifact_output_map.py --summary-only
	$(PYTHON) scripts/build_artifact_output_map.py --write --summary-only
	$(PYTHON) scripts/validate_artifact_output_map.py --summary-only
	$(PYTHON) scripts/validate_cross_surface_consistency.py --mode strict --summary-only
	$(PYTHON) scripts/validate_slice_lifecycle.py --mode strict
	$(PYTHON) scripts/validate_future_note_materiality.py --mode strict
	$(PYTHON) scripts/validate_runtime_governance_dirs.py --summary-only
	$(PYTHON) scripts/validate_no_secrets_persisted.py --mode strict --summary-only
	$(PYTHON) scripts/validate_receipts_checkpoints.py --summary-only
	$(PYTHON) scripts/validate_source_provenance.py

render:
	$(PYTHON) scripts/render_canonical_entrypoints.py --write

render-check:
	$(PYTHON) scripts/render_canonical_entrypoints.py --check

test:
	$(PYTHON) -m pytest -q tests
	cd examples/minimal_repo && $(PYTHON) -m pytest -q tests
	cd examples/small_config_tool_repo && $(PYTHON) -m pytest -q tests

validate-examples:
	$(PYTHON) scripts/validate_low_token_workflow.py --summary-only
	$(PYTHON) scripts/validate_source_read_register.py --summary-only
	$(PYTHON) scripts/validate_planned_future_surfaces.py --summary-only
	$(PYTHON) scripts/build_repo_file_index.py --summary-only
	$(PYTHON) scripts/build_command_map.py --summary-only
	$(PYTHON) scripts/query_command_map.py --safe-read-only --summary-only
	$(PYTHON) scripts/validate_command_map.py --summary-only
	$(PYTHON) scripts/validate_claude_integration.py --summary-only
	$(PYTHON) scripts/validate_read_only_commands.py --summary-only
	$(PYTHON) scripts/build_plan_note_index.py --summary-only
	$(PYTHON) scripts/build_artifact_output_map.py --summary-only
	$(PYTHON) scripts/validate_artifact_output_map.py --summary-only
	$(PYTHON) scripts/validate_runtime_governance_dirs.py --summary-only
	$(PYTHON) scripts/validate_no_secrets_persisted.py --summary-only
	$(PYTHON) scripts/validate_receipts_checkpoints.py --summary-only
	$(PYTHON) scripts/build_repo_file_index.py --root examples/small_config_tool_repo --summary-only
	$(PYTHON) scripts/validate_slice_packet.py examples/minimal_repo/plans/slices/slice_001_packet.json --summary-only
	$(PYTHON) scripts/validate_slice_packet.py examples/small_config_tool_repo/plans/slices/slice_001_packet.json --summary-only
	cd examples/small_config_tool_repo && $(PYTHON) scripts/validate_greeting_config.py configs/greeting_config.json --summary-only

release-check:
	$(PYTHON) -m json.tool repo_agnostic_durable_slice_build_workflow_methodology_20260514.json >/dev/null
	$(PYTHON) -m json.tool contracts/low_token_workflow_contract.json >/dev/null
	$(PYTHON) -m json.tool contracts/command_map_contract.json >/dev/null
	$(PYTHON) -m json.tool plans/source_read_register.json >/dev/null
	$(PYTHON) -m json.tool plans/planned_future_surfaces.json >/dev/null
	$(PYTHON) -m json.tool schemas/methodology.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/slice_packet.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/refresh_decision.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/low_token_workflow_contract.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/repo_file_index.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/command_map.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/mature_repo_migration_packet.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/read_only_command_harness.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/source_read_register.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/planned_future_surfaces.schema.json >/dev/null
	$(PYTHON) -m json.tool contracts/read_only_command_harness.json >/dev/null
	$(PYTHON) -B -c "import pathlib,tomllib; tomllib.loads(pathlib.Path('pyproject.toml').read_text())"
	@if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then git diff --check; else echo "SKIP git diff --check (not a git repo)"; fi
	$(PYTHON) scripts/validate_claude_integration.py --summary-only
	$(PYTHON) scripts/validate_release_package.py --summary-only

repo-index:
	$(PYTHON) scripts/build_repo_file_index.py --write --summary-only

repo-index-check:
	$(PYTHON) scripts/build_repo_file_index.py --check --summary-only

read-only-check:
	$(PYTHON) scripts/validate_read_only_commands.py --run --summary-only

bootstrap-smoke:
	$(PYTHON) scripts/bootstrap_local_repo.py /tmp/durable-slice-bootstrap-smoke --project-name durable-slice-bootstrap-smoke --force
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/render_canonical_entrypoints.py --check
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/validate_low_token_workflow.py --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/validate_source_read_register.py --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/validate_planned_future_surfaces.py --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/build_repo_file_index.py --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/build_command_map.py --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/query_command_map.py --safe-read-only --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/validate_command_map.py --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/validate_claude_integration.py --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/validate_read_only_commands.py --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/validate_release_package.py --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) -m pytest -q tests

clean:
	rm -rf .pytest_cache scripts/__pycache__ tests/__pycache__
	rm -rf examples/minimal_repo/scripts/__pycache__ examples/minimal_repo/tests/__pycache__
	rm -rf examples/small_config_tool_repo/scripts/__pycache__ examples/small_config_tool_repo/tests/__pycache__
