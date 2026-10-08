# Morning briefing evaluation onboarding

This document describes the scorer development branch `sana/morning-brief-scorers-on-pr109`. The workflow source and its first-run/full-run distinction are in [Chief of Staff morning briefing steps](chief-of-staff-morning-briefing-steps.md). The exact skill inside the pinned SAW image has not been independently inspected; confirm it before treating the local image checkout as the definitive runtime contract.

## What this evaluation observes

- The scene in `submissions/openclaw-forge/scenes/monday-acquisition.yaml` names the test M365 account. Its mailbox is seeded outside this evaluation. Expected Watson/Contoso items must be checked against collected evidence before treating their absence as an agent recall failure.
- The agent's final chat response and Forge's published `brief.json` are separate outputs. On a first run, an attention brief may be published and then replaced by a full brief at the same path; only the last artifact remains. The event sequence is needed to assess the attention publication.
- Execution, full publication, content quality, and latency are separate results. An `exec` tool call is an attempt, not proof that its script succeeded. Match each call to its `tool_result` by `tool_use_id` and inspect the result or saved artifact.
- The morning-briefing quality judges in `submissions/openclaw-forge/eval.yaml` currently score the final response. They do not by themselves verify the content of the published cards.

## Workflow scorer inventory

Implement the **planned** checks one at a time after confirming which observations the harness reliably preserves. Existing checks should be reviewed for case scope and evidence limits. All full-brief checks are for the morning-briefing case, not the analysis-panel case.

| Scorer | Status and applicability | Entities and proof sought |
| --- | --- | --- |
| `used_catalog_skills` | Existing | In `outputs.events`, match `read` calls for the daily-briefing and Microsoft 365 `SKILL.md` paths to non-error `tool_result` entries by call ID. Reading is distinct from following the instructions. |
| `used_m365_tools` | Existing; case condition needs review | Match an `exec` call for `collect-brief-evidence.mjs` to its result; inspect saved sealed `brief.evidence.json` and `brief.index.json` for the expected account, retrieved M365 records, matching evidence IDs, and observed counts. Its current condition depends on `expected_top_of_mind`; that should be decoupled from disputed mailbox expectations. |
| `attention_brief_published` | Planned; only when the collector identifies a first run | In events, pair the first sweep, seal, attention compose, and publisher calls with results. Require the publisher's disk read-back to report `scope: attention` and the attention evidence ID. The final `brief.json` cannot establish this because it is replaced. |
| `continued_to_full_run` | Planned; first run only | Require a new full sweep after successful attention publication, within the same case event sequence. The full sweep has a new evidence ID. |
| `full_evidence_sealed` | Planned | Match the full sweep and `seal` calls to results; check the saved evidence manifest is sealed and has the same evidence ID as the index. |
| `full_batches_reviewed` | Planned; per sealed batch plan | Compare the manifest's declared batches with `sessions_spawn` calls for `brief-reader`, batch result files, and the parent agent's `read` calls/results. Allow retries. No batch calls are required when the sealed plan contains no batches. |
| `full_candidate_composed` | Planned | Match `exec` for `compose-brief.mjs` to a successful result reporting full composition for the sealed full-run evidence ID. A failed attempt followed by a successful retry can pass. |
| `full_publisher_succeeded` | Planned | Match `exec` for `publish-brief.mjs` to a success/read-back result with `scope: full` and the full-run evidence ID; compare with the saved final artifact. A publisher call alone does not pass. |
| `full_workflow_order` | Planned | Compare event positions for full sweep, seal, batch work when declared, successful compose, and successful publisher read-back; verify the same full-run evidence ID across stages. |
| `published_brief` | Existing | Inspect saved `brief.json`, sealed evidence, and index for full scope, required Forge v1 structure, and matching evidence IDs. This verifies the final artifact; it does not prove which agent actions produced it or that its chosen items are useful. |
| `response_received` | Existing | Match the delivered `outputs.output_content` with the final parent assistant event; reject empty or `NO_REPLY` responses. This is distinct from publication. |

### Conditional work and quality

Slack context drills apply only when the selected source and relevant conversations call for them. Forge proposal list/create/revise/show operations depend on tool availability and whether a proposal is warranted. They should not be mandatory in every run. Attention checks are not applicable to a refresh that starts with an existing brief.

Separate quality scorers are needed for ranking, factual grounding, source quotes, and whether the chosen cards serve the executive. The workflow checks above answer whether the required steps completed, not whether the brief is good.

### Evidence gaps to settle before coding

The archived diagnostic `events.json` redacts some long tool results. In that run, the attention publisher's read-back is visible, while the full publisher's result is redacted. A scorer must not infer publisher success from `is_error: false` alone: an `exec` result can still contain a shell command failure. Confirm whether other retained output proves full publisher read-back; if it does not, capture a compact status artifact in a future run. Likewise, confirm that every batch result and the first-run/full-run signal is available to the scorer before requiring it. Missing observations should be reported as insufficient evidence, not silently counted as success.

## Implementation sequence

1. Confirm the runtime skill version and the event/artifact data available to each scorer. Decide how first-run checks report *not applicable*.
2. Implement and test `attention_brief_published`, then `continued_to_full_run` against archived first-run and refresh cases.
3. Implement and test full-run sealing, batch review, composition, publisher completion, and ordering one at a time, allowing valid retries and conditional branches.
4. Review existing scorer conditions, then develop content-quality and latency measures separately from workflow completion.

Do not start a new PipelineRun solely to test these definitions until the scorer and its required artifacts have been validated locally.
