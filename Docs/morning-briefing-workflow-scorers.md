# Morning briefing workflow checks

These checks score observable execution separately from brief quality and
latency. They apply to the `morning-briefing` case through its
`requires_published_brief` annotation. The `analysis-panel` case has a
different workflow and is not covered by the full-brief checks.

The workflow map follows the current `openclaw-saw-image` daily-briefing skill
and publisher at local source commit `e7291b7`, plus the archived
`sana-morning-briefing-collector-diag-cfqt2` event trace. The flow repo's
vendored `workspace/skills/daily-briefing/SKILL.md` is an older snapshot;
`eval.yaml` provisions no workspace files, so the selected SAW image supplies
the runtime skill. The exact pinned GHCR digest could not be inspected without
registry access. Recheck its skill before treating this map as an image-version
contract.

| Skill stage | Check in `eval.yaml` | What it establishes |
| --- | --- | --- |
| Read daily-briefing and M365 skill files | `used_catalog_skills` | Matched `read` calls and tool results for both files. |
| Sweep governed M365 evidence | `used_m365_tools` | Collector call/result plus sealed M365 records, account, and observed coverage. |
| Seal the evidence | `sealed_brief_evidence` | `seal` call/result and a sealed manifest whose ID matches the index. |
| Fan out and read declared batch results | `reviewed_brief_batches` | Every sealed batch has an accepted `brief-reader` spawn and a parent read-back with the current evidence ID. Zero batches require no fan-out. |
| Compose the full candidate | `composed_full_brief` | Matched composer call and success message naming the final brief's evidence ID. Retries are allowed. |
| Invoke the publisher after full composition | `called_brief_publisher` | Matched publisher call/result after successful full composition. This is invocation, not proof of a zero shell exit. |
| Preserve full-run stage order | `full_brief_stage_order` | Sweep before seal, batch work (when present) before composition, and publisher call after successful full composition. |
| Publish the complete brief | `published_brief` | The collected `brief.json` has full scope, required Forge v1 structure, and IDs/coverage matching the sealed artifacts. |
| Return a final response | `response_received` | A final parent assistant message matches delivered text and is not `NO_REPLY`. |

The first-run attention brief is an intermediate product; the full brief is the
required outcome. Context drills are conditional on relevant Slack threads.
Forge draft list/show/create/revise operations are conditional on proposal
availability and decisions. Their correctness requires separate, conditional
checks rather than mandatory calls in every run.

`events.json` can redact long results. An `exec` tool result with
`is_error: false` may still contain `(Command exited with code 1)`, so a call
alone is never counted as successful composition or publication. The publisher
also validates source quotes, draft state, and freshness inside the sandbox;
the final-artifact check does not independently repeat those validations.
