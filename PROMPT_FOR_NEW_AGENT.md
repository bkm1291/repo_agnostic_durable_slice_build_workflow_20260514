# Prompt For New Agent

Use this when you want to hand a repo and a project goal to a fresh agent.

Shortest beginner prompt:

```text
Read this folder and use it as the workflow template for my repo.

I authorize you to inspect the files in this folder.

If I name a target repo path or folder, I authorize you to create that folder if needed, copy or bootstrap this workflow into it, and create or update only the starter roadmap and first slice packet before coding. If I say current repo, current folder, current one, or you are already working inside an empty target folder, use the current working directory as the target. If no target repo path or folder is clear, ask me for it before writing files.

First read README.md, START_HERE.md, AGENTS.md, and `PROJECT_GOAL.md` if it exists. If `PROJECT_GOAL.md` has a real non-placeholder goal, use it automatically. If it is missing or still placeholder text, ask me exactly: "What do you want to build? One or two paragraphs is enough."

After the goal is known, create or update the roadmap and first slice packet, then validate the packet. Do not create app/source implementation files or code features until the packet validates. Do not code until the packet validates.
```

No-prompt path: copy `PROJECT_GOAL.template.md` to `PROJECT_GOAL.md`, fill in
the goal, then give the folder to the agent and paste the prompt above.

Copy the block below into the new agent. Replace the bracketed values first.

```text
You are working in this local repo:

[ABSOLUTE_REPO_PATH]

Project goal:

[ONE OR TWO PARAGRAPHS DESCRIBING WHAT THE REPO SHOULD BUILD]

Current requested slice:

[THE SMALLEST NEXT PIECE OF WORK, OR "create the first roadmap and slice packet from the project goal"]

Constraints:

- Work only inside [ABSOLUTE_REPO_PATH] unless I explicitly approve another path.
- Treat sibling repos, vendor folders, downloads, archives, and external data roots as read-only unless I explicitly approve mutation.
- Do not rely on chat as future authority. Save important decisions in repo files.
- Keep the work low-token: query or inspect file inventory before broad reads, keep reads targeted, and use compact validator output.
- Do not refresh generated indexes or catalogs unless the slice packet's refresh_decision requires it.
- Commit implementation before generated refresh outputs if generated refresh is required.
- Do not chase head-only generated-index staleness.

Startup:

1. Read AGENTS.md.
2. Read CLAUDE.md if using Claude Code.
3. Read SKILL.md if present.
4. Read README.md and START_HERE.md if this repo is newly bootstrapped.
5. Read repo_agnostic_durable_slice_build_workflow_methodology_20260514.json.
6. Read PROJECT_GOAL.md if it exists. If it contains a real non-placeholder goal, use it as the project goal.
7. Read plans/repo_roadmap.json and the selected plans/slices/*_packet.json if they exist.
8. If the packet cites source_read:<id>, read plans/source_read_register.json.
9. If the packet cites planned future surface ids, read plans/planned_future_surfaces.json.
10. Run python scripts/build_command_map.py --summary-only, python scripts/query_command_map.py --safe-read-only --summary-only, and python scripts/validate_command_map.py --summary-only before adding new commands or helpers.
11. Run python scripts/validate_claude_integration.py --summary-only if using Claude Code or modifying Claude surfaces.
12. If this is an existing mature repo, stop and read docs/MIGRATING_MATURE_REPO.md before copying or adapting template files.
13. Check git status before editing.

Claude Code shortcut:

- Run /skills.
- Use /durable-slice for normal roadmap/slice/implementation work.
- Use /durable-slice-audit for read-only review.
- Use /durable-slice-release only when I explicitly ask for release work.

If there is no roadmap or packet:

- If PROJECT_GOAL.md contains a real non-placeholder goal, use it automatically.
- If the project goal is missing, vague, or still a placeholder, ask: "What do you want to build? One or two paragraphs is enough." Do not create or update a roadmap, packet, or code until the goal is known.
- Create plans/repo_roadmap.json.
- Create plans/slices/slice_001_packet.json.
- Keep the first slice small enough to name owner files, owner configs/schemas/contracts, source reads, owning validator, focused tests, not-in-scope items, boundary_rules, refresh_decision, and commit_plan before coding.
- Run python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only.

Build rules:

- Implement only files named in files_to_create_or_edit.
- If the needed owner files change, update and revalidate the packet before editing.
- Add or update the owning validator.
- Add focused tests for the selected slice.
- Keep runtime-affecting values in config, schema, contract, policy, or explicit operator selection.
- Keep future features in not_in_scope and boundary_rules unless this slice explicitly owns them.

Validation:

Run the focused commands from focused_validators_and_tests, then run:

python scripts/render_canonical_entrypoints.py --check
python scripts/validate_low_token_workflow.py --summary-only
python scripts/validate_source_read_register.py --summary-only
python scripts/validate_planned_future_surfaces.py --summary-only
python scripts/build_command_map.py --summary-only
python scripts/query_command_map.py --safe-read-only --summary-only
python scripts/validate_command_map.py --summary-only
python scripts/validate_claude_integration.py --summary-only
python scripts/validate_read_only_commands.py --summary-only
python scripts/validate_release_package.py --summary-only
python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only
python -m pytest -q tests
git diff --check
git status --short

Closeout:

- Summarize files changed.
- Summarize validation commands and results.
- State whether generated refresh was required and whether it was run.
- State remaining risks or the next recommended slice.
- Do not leave important future requirements only in chat.
```
