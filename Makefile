PYTHON ?= python

.PHONY: check render render-check test validate-examples clean bootstrap-smoke release-check

check: render-check validate-examples test release-check

render:
	$(PYTHON) scripts/render_canonical_entrypoints.py --write

render-check:
	$(PYTHON) scripts/render_canonical_entrypoints.py --check

test:
	$(PYTHON) -m pytest -q tests
	cd examples/minimal_repo && $(PYTHON) -m pytest -q tests
	cd examples/small_config_tool_repo && $(PYTHON) -m pytest -q tests

validate-examples:
	$(PYTHON) scripts/validate_slice_packet.py examples/minimal_repo/plans/slices/slice_001_packet.json --summary-only
	$(PYTHON) scripts/validate_slice_packet.py examples/small_config_tool_repo/plans/slices/slice_001_packet.json --summary-only
	cd examples/small_config_tool_repo && $(PYTHON) scripts/validate_greeting_config.py configs/greeting_config.json --summary-only

release-check:
	$(PYTHON) -m json.tool repo_agnostic_durable_slice_build_workflow_methodology_20260514.json >/dev/null
	$(PYTHON) -m json.tool schemas/methodology.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/slice_packet.schema.json >/dev/null
	$(PYTHON) -m json.tool schemas/refresh_decision.schema.json >/dev/null
	$(PYTHON) -B -c "import pathlib,tomllib; tomllib.loads(pathlib.Path('pyproject.toml').read_text())"
	@if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then git diff --check; else echo "SKIP git diff --check (not a git repo)"; fi

bootstrap-smoke:
	$(PYTHON) scripts/bootstrap_local_repo.py /tmp/durable-slice-bootstrap-smoke --project-name durable-slice-bootstrap-smoke --force
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/render_canonical_entrypoints.py --check
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
	cd /tmp/durable-slice-bootstrap-smoke && $(PYTHON) -m pytest -q tests

clean:
	rm -rf .pytest_cache scripts/__pycache__ tests/__pycache__
	rm -rf examples/minimal_repo/scripts/__pycache__ examples/minimal_repo/tests/__pycache__
	rm -rf examples/small_config_tool_repo/scripts/__pycache__ examples/small_config_tool_repo/tests/__pycache__
