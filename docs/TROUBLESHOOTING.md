# Troubleshooting

This guide maps common starter failures to the next useful fix.

## `PACKET_MISSING_FIELD`

The slice packet is missing a required field.

Open the packet and add the named field. Compare with
`docs/ANNOTATED_SLICE_PACKET.md` if the field is unfamiliar.

## `PACKET_FIELD_VAGUE`

A field says something like `TBD`, `maybe`, or `if needed`.

Replace it with a concrete statement. A beginner-safe packet should say exactly
what will be built, what proves it, and what is out of scope.

## `PACKET_PATH_NOT_REPO_RELATIVE`

The packet contains an absolute path or a path with `..`.

Use paths relative to the repo root:

```json
"scripts/validate_slice_packet.py"
```

Do not use:

```json
"/home/me/project/scripts/validate_slice_packet.py"
```

## `SOURCE_READ_EVIDENCE_CHAT_ONLY`

The packet uses chat, memory, or conversation as proof.

Replace it with a repo file, local contract, schema, README, indexed file, or
other durable local evidence.

## `SOURCE_READ_EVIDENCE_EMPTY`

A required source read says it was needed, but does not name the evidence.

Add an `evidence_ref`, or set `read_type` to `none` and `status` to
`not_required` when the read is truly unnecessary.

## `SOURCE_READ_REGISTER_REF_NOT_FOUND`

The packet cites `source_read:<id>`, but that id is not present in
`plans/source_read_register.json`.

Add the source read to the register, or change the packet to cite a durable repo
file directly.

## `BOUNDARY_RULES_NOT_OBJECT`

The packet is missing machine-checkable boundary rules.

Add `boundary_rules` with allowed scope, forbidden path prefixes, forbidden
keywords, and planned future surface ids. Use empty arrays only when there is
truly nothing to forbid or defer.

## `BOUNDARY_FORBIDDEN_PATH_PREFIX_MATCH`

The packet tries to edit a path under a forbidden prefix such as `manifests/` or
`receipts/`.

Either remove that path from the slice, or make the generated/index work its own
explicit slice with a non-skip refresh decision.

## `BOUNDARY_PLANNED_SURFACE_WRONG_OWNER`

The packet tries to create or edit a future surface owned by another slice.

Open `plans/planned_future_surfaces.json`. Either activate the owning slice, or
keep this surface in `not_in_scope`.

## `FOCUSED_COMMANDS_MISSING_OWNING_VALIDATOR`

The focused commands do not run the validator named by `owning_wave_validator`.

Add the validator command to `focused_validators_and_tests`.

## `FOCUSED_COMMANDS_MISSING_OWNING_TEST`

The focused commands do not run one of the tests named by `owning_wave_tests`.

Add a test command that references the test path.

## `FOCUSED_COMMANDS_CONTAIN_WRITE_INTENT`

A focused proof command appears to write files, force changes, delete files, or
redirect output.

Focused proof should normally be read-only. Move writer commands into an
explicit implementation or generated-refresh step.

## `REFRESH_REQUIRED_WITH_SKIP_TIMING`

At least one refresh flag is true, but `refresh_timing` is `skip`.

Choose a non-skip timing such as `after_implementation_commit`, or set the
refresh flags to false if no generated discovery is needed.

## `REFRESH_NOT_REQUIRED_WITH_NON_SKIP_TIMING`

No refresh flag is true, but `refresh_timing` is not `skip`.

Set `refresh_timing` to `skip`, or explain which generated surface must refresh
by setting the correct flag to true.

## `REFRESH_FLAG_REASON_MISSING_KEYWORD`

A refresh flag is true, but the reason does not explain that kind of refresh.

Example: if `config_variable_inventory_required` is true, the reason should
mention config, variables, or runtime fields.

## `COMMIT_PLAN_REFRESH_REQUIRED_BUT_GENERATED_COMMIT_NOT_REQUIRED`

The packet says a generated refresh is required, but the commit plan says no
generated refresh commit is needed.

Name the generated refresh commit in `generated_refresh_commit`.

## `LOW_TOKEN_TARGETED_READ_LIMIT_TOO_HIGH`

The low-token contract allows reads broader than the template default.

Keep normal targeted reads at or below 120 lines unless the target repo has a
deliberate local policy.

## `READ_ONLY_COMMAND_MODIFIED_PATHS`

The read-only command harness ran a command and detected file changes.

Move that command out of the read-only harness, or change the command so it uses
a check/status/summary mode that does not write files.

## `READ_ONLY_COMMAND_GIT_PORCELAIN_CHANGED`

The command changed `git status --porcelain` output.

Treat this as a side effect even if file hashes look harmless. Move the command
out of the read-only harness or make it a true status/check command.

## `READ_ONLY_COMMAND_SECRET_OUTPUT`

The command printed something that looks like a credential, token, private key,
or secret assignment.

Do not paste the raw output into reports. Fix the command to redact sensitive
values before it is allowed in the read-only harness.

## `COMMAND_MAP_WRITER_WITHOUT_EXPLICIT_INTENT`

The command map found a writer command that does not require explicit writer
intent.

Mark the command as `write_explicit` and set
`writer_mode_requires_explicit_intent` to true, or remove write flags from the
command.

## `COMMAND_MAP_HARNESS_WRITER_UNSAFE`

A command marked safe for the read-only harness is also classified as a writer.

Writers do not belong in the read-only harness. Move the command to an explicit
writer workflow or change it to a true summary/check mode.

## `MIGRATION_HIGH_RISK_AUTHORITY_UNCLASSIFIED`

A mature-repo migration packet did not classify one of the target repo's
high-risk authority files such as `AGENTS.md`, `SKILL.md`, `README.md`, or
`pyproject.toml`.

Read that file in the target repo and add it to
`existing_authority_surfaces` before migration.

## `MIGRATION_TEMPLATE_SURFACE_OVERWRITES_PROTECTED_PATH`

The migration packet allows a template file to overwrite a protected target
path.

Either change the target path, set `overwrite_allowed` to false, or get exact
operator approval and update the packet scope.

## `RELEASE_REQUIRED_PATH_MISSING`

The release package validator expected a public template file, script, schema,
contract, test, example, or CI workflow and could not find it.

Restore the missing file, or update `scripts/validate_release_package.py` only
if the file is intentionally no longer part of the public release surface.

## `RELEASE_TRACKED_SCRATCH_OR_CACHE_PATH`

A scratch, temporary, or cache path is tracked or would be packaged.

Remove it from the release surface and keep it covered by `.gitignore`.

## `RELEASE_CHANGELOG_VERSION_MISMATCH`

`pyproject.toml` and `CHANGELOG.md` disagree about the release version.

Update the changelog entry before tagging or publishing.

## First Debug Command

When unsure, run:

```bash
make check
```

Then fix the first failure before chasing later output.
