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

## First Debug Command

When unsure, run:

```bash
make check
```

Then fix the first failure before chasing later output.
