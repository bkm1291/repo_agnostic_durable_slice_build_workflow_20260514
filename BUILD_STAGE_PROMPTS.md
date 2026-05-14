<!-- GENERATED FROM repo_agnostic_durable_slice_build_workflow_methodology_20260514.json BY scripts/render_canonical_entrypoints.py. EDIT THE JSON, THEN RUN --write. -->

# Durable Build Stage Prompts

Use these prompts inside a brand-new repo bootstrapped from this bundle. They are
operator-facing prompt surfaces derived from
`repo_agnostic_durable_slice_build_workflow_methodology_20260514.json`.

Do not use this prompt file to override a mature repo's existing rules.

## Usage Rule

Use long form when starting a new agent, when automatic project-doc injection is
uncertain, or when protected/runtime/source/safety surfaces are involved. Use
short form only when `AGENTS.md`, `SKILL.md`, the durable methodology, and the
active roadmap are already available to the agent.

## Long Form Readiness Prompt

```text
Use the durable slice workflow foundation. Read AGENTS.md, SKILL.md, the durable methodology, the active roadmap or owner plan for the whole wave chain, the selected <wave_id> section, and any dependency/future-wave notes that mention <wave_id>. Check worktree state and classify stale generated outputs as evidence unless a required validator/test or hard safety invariant fails. Is <wave_id> ready to implement, or is there one compact prep action that would make future slices easier? Confirm owner files, owning validator, focused tests, required source reads, not-in-scope boundaries, structured refresh decision, and commit shape. Do not implement yet unless readiness is clear.
```

## Long Form Slice Packet Prompt

```text
Use the durable slice workflow foundation. Create or confirm the compact slice packet for <wave_id> from <owner_plan_ref>. The packet must name selected wave/slice, files to create or edit, owner configs/schemas/contracts/policies/modules/scripts/tests, required source reads or explicit no-new-source-read statement, owning validator, focused tests, not-in-scope boundaries, future-note rules, structured refresh decision, implementation commit plan, and generated refresh commit plan if required. Keep this tactical; do not create a new broad architecture plan.
```

## Long Form Implementation Prompt

```text
Use the durable slice workflow foundation. Read AGENTS.md, SKILL.md, the durable methodology, <owner_plan_ref>, the selected <wave_id> section, dependency/future notes for <wave_id>, and the compact slice packet. Confirm owner files, owning validator, focused tests, required source reads, not-in-scope boundaries, structured refresh decision, and commit shape before editing. Implement only the owner bundle. Use existing helpers/indexes/catalogs/patterns before creating new helpers. Keep runtime-affecting values config-owned or explicitly operator-selected. Add or update the owning validator and focused tests. Persist only discoveries that change future implementation order, owner files, validators, tests, source reads, safety boundaries, refresh decisions, helper reuse, activation gates, receipts, or closeout. Run focused proof. Commit implementation first. Refresh generated indexes only if the packet requires it, commit generated outputs once, and stop without head-chasing.
```

## Focused Proof Prompt

```text
Use the durable slice workflow foundation. For <wave_id>, run changed structured-file parse where relevant, the owning validator, focused tests, read-only/no-write checks where relevant, no-secret/no-token checks where relevant, and diff/worktree checks. Treat broad index/status checks as navigation evidence unless this wave owns them. Fix owner failures instead of weakening tests. Report exact commands and results.
```

## Generated Refresh Prompt

```text
Use the durable slice workflow foundation. Read the structured refresh decision for <wave_id>. If refresh is required, run only the named generated index/catalog/inventory/projection hooks from the implementation head, validate generated outputs, commit generated outputs once, and stop. If only head-only staleness remains after the generated commit, classify it as evidence and do not refresh again.
```

## Closeout Prompt

```text
Use the durable slice workflow foundation. Close out <wave_id> by reporting implementation commit, generated-refresh commit if any, validation commands/results, worktree state, classified residual noise, future-affecting notes persisted, and whether the next wave is ready. Confirm no future requirement remains only in chat. Do not create a closeout receipt unless it proves a writer, generator, materializer, external action, irreversible operation, release gate, or phase closeout.
```

## Short Form Prompts

### Readiness Prompt

```text
Is wave X ready to implement, or is there anything else we should do to make future slices easier? Read the full active roadmap/owner plan for this wave chain, dependency/future-wave notes, and build a compact slice packet if ready.
```

### Implementation Prompt

```text
Implement wave X from the compact slice packet. During closeout, note anything that affects future wave implementation, update durable JSON only when it changes future order/owners/validators/full-read needs/safety/index/activation gates, then validate and commit.
```
