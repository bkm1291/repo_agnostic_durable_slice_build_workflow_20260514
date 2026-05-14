# Migrating A Mature Repo

Use this guide only when adopting the durable slice workflow into an existing
repo that already has its own rules, plans, scripts, generated outputs, or
release process.

Do not copy this template over a mature repo by habit. A migration must preserve
the target repo's current authority until an explicit migration packet says what
will be kept, adapted, skipped, or superseded.

## Required Rule

Create and validate a mature-repo migration packet before changing the target
repo.

```bash
python scripts/validate_mature_repo_migration_packet.py <packet> --summary-only
```

The packet schema is:

```text
schemas/mature_repo_migration_packet.schema.json
```

## Safe Migration Sequence

1. Read the target repo's existing `AGENTS.md`, `SKILL.md`, README, roadmap,
   release notes, CI, and local safety policies.
2. Record those files in `existing_authority_surfaces`.
3. Mark protected or forbidden paths in `protected_paths`.
4. Choose `adoption_mode`.
5. List every template surface as `copy`, `adapt`, or `skip`.
6. Keep overwrite disabled unless the operator has approved that exact path.
7. Validate the packet.
8. Migrate only the approved surfaces.
9. Run the target repo's original checks and the newly adopted checks.
10. Commit migration changes separately from later feature work.

## Adoption Modes

- `reference_only`: keep this template as documentation or a sidecar reference.
- `copy_subset`: copy a small set of starter files into the target repo.
- `adapt_in_place`: adapt selected workflow ideas to the target repo's existing
  authority surfaces.
- `full_template_migration`: replace broad workflow surfaces. Use this only with
  explicit operator approval for the exact paths being replaced.

## Schema-Vs-Validator Authority

Schemas define JSON shape, required fields, allowed enum values, and portable
structural constraints.

Python validators define semantic rules, cross-file rules, side-effect rules,
read-only checks, and local adoption safety.

If the schema accepts a packet but the Python validator rejects it, the
validator rejection blocks migration until the packet or schema is intentionally
updated.

## Minimal Packet Shape

```json
{
  "schema_version": "v1.repo_agnostic_mature_repo_migration_packet.1",
  "migration_id": "example_mature_repo_migration",
  "status": "ready",
  "target_repo_path": "/absolute/path/to/target-repo",
  "operator_goal": "Adopt the durable slice workflow without overwriting existing authority.",
  "adoption_mode": "copy_subset",
  "existing_authority_surfaces": [
    {
      "path": "AGENTS.md",
      "authority_class": "agent_rules",
      "status": "keep",
      "migration_action": "keep",
      "evidence_ref": "AGENTS.md"
    }
  ],
  "protected_paths": [
    "AGENTS.md",
    "SKILL.md",
    ".github/workflows/"
  ],
  "allowed_mutation_roots": [
    "docs/",
    "plans/"
  ],
  "planned_template_surfaces": [
    {
      "source_path": "PROMPT_FOR_NEW_AGENT.md",
      "target_path": "docs/PROMPT_FOR_NEW_AGENT.md",
      "action": "adapt",
      "overwrite_allowed": false,
      "reason": "Add handoff guidance without replacing target repo rules."
    }
  ],
  "required_preflight_commands": [
    "git status --short",
    "python -m pytest -q"
  ],
  "validation_commands": [
    "python scripts/validate_mature_repo_migration_packet.py plans/migration_packet.json --summary-only"
  ],
  "risk_register": [
    "Existing AGENTS.md remains authoritative until an exact replacement is approved."
  ],
  "approval": {
    "explicit_operator_approval_required": true,
    "approval_scope": "Approve only the listed planned_template_surfaces paths."
  }
}
```
