<!-- GENERATED FROM repo_agnostic_durable_slice_build_workflow_methodology_20260514.json BY scripts/render_canonical_entrypoints.py. EDIT THE JSON, THEN RUN --write. -->

# Claude Code Entry Point

@AGENTS.md

Claude Code reads `CLAUDE.md` at session start. Keep this file short; the durable
workflow doctrine stays in `AGENTS.md`, `SKILL.md`, and
`repo_agnostic_durable_slice_build_workflow_methodology_20260514.json`.

## Start Here

1. If this workflow is new, read `START_HERE.md`.
2. If the user is handing you a project goal, use `PROMPT_FOR_NEW_AGENT.md` as the one-time setup shape.
3. Check `PROJECT_GOAL.md` first. If it exists and contains a concrete non-placeholder goal, use it automatically. If the user says only "use this", "use this template", gives a placeholder goal, or `PROJECT_GOAL.md` is missing/placeholder-only, ask exactly: "What do you want to build? One or two paragraphs is enough." Do not create or update a roadmap, packet, or code until the goal is known.
4. Run `/skills` and confirm these project skills are available:
   - `/durable-slice` from `.claude/skills/durable-slice/SKILL.md`
   - `/durable-slice-audit` from `.claude/skills/durable-slice-audit/SKILL.md`
   - `/durable-slice-release` from `.claude/skills/durable-slice-release/SKILL.md`
5. Create or validate `plans/repo_roadmap.json` and `plans/slices/slice_001_packet.json` before coding.
6. Run `python scripts/validate_slice_packet.py plans/slices/slice_001_packet.json --summary-only` before implementation.
7. Run `python scripts/validate_claude_integration.py --summary-only` when checking this integration.

## Claude Skills

- `/durable-slice <project goal or slice request>`: start or continue the roadmap -> slice packet -> implementation -> validation loop.
- `/durable-slice-audit <audit focus>`: run a read-only audit in isolated context and return concise findings.
- `/durable-slice-release <version or release focus>`: manually run release-readiness checks from `RELEASE_CHECKLIST.md`.

## Claude-Specific Safety

- Do not add `.claude/settings.json` hooks or `.mcp.json` servers unless a later repo explicitly owns that integration.
- Do not add broad `allowed-tools` to project skills; let Claude Code permissions and the user control tool approval.
- Do not mutate sibling repos, vendor folders, downloads, archives, or external data roots unless the user explicitly approves that exact path.
- If a mature repo already has Claude authority files, stop and use `docs/MIGRATING_MATURE_REPO.md` before copying this template over them.

## Closeout

Report changed files, validation commands/results, worktree state, whether generated refresh was required, and the next recommended slice. Do not leave future requirements only in chat.

This template is build governance, not a prompt chain. Use the initial install/setup prompt only to establish repo authority. After that, preserve the current agent thread, reason from repo-native artifacts, and follow the roadmap -> slice packet -> validator -> focused tests -> closeout structure without emitting recurring operator prompt instructions.

After the initial roadmap and first slice packet validate, report that the packet is ready and do not create app/source implementation files unless the current user request explicitly activates implementation.

After an implementation slice passes proof, close out with changed files, validation results, generated-refresh decision, worktree state, residual risks, and the next governed action from the roadmap. The next slice still requires a valid packet before implementation.
