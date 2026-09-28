# Morning briefing harness and evaluation change log

This is the project record for changes to Sana's `agent-eval-harness` fork and
`agentic_eval_flow` fork that affect the OpenShell Chief of Staff evaluation.
Add a dated entry for each new source change, with its commit, the run that used
it (if any), and what that run actually proved. PipelineRun YAML under
`tmp/runs/` is a local request until submitted; a branch name can move, so use
the resolved commit from the TaskRun setup log when recording run evidence.

## Current pins — 2026-09-28

| Component | Revision | State |
| --- | --- | --- |
| Evaluation definitions | [`2194681`](https://github.com/sanafayyaz315/agentic_eval_flow/commit/219468160921758740e9eadcc8a904029808e504) on `sana/morning-brief-eval` | Published; morning-only case, Flash `maxTokens: 128000`, and `llm_preflight_max_tokens: 512`. |
| Gateway harness used by the cap-50 and cap-100 runs | [`7ac4356`](https://github.com/sanafayyaz315/agent-eval-harness/commit/7ac43562bf91e9d1afd8bdf3c1abf7f908fca119) on `fix/openclaw-brief-reader-eval-config` | Published; includes per-turn and case token-usage logs. |
| Configurable preflight harness | [`adde054`](https://github.com/sanafayyaz315/agent-eval-harness/commit/adde05406aaabcd63b1bfe6eecd93fd564973265) on `fix/configurable-openclaw-preflight-tokens` | Published on a separate branch; no PipelineRun using this commit is recorded here. |
| Sandbox image for Gateway comparisons | `ghcr.io/sanafayyaz315/openclaw-saw-agent@sha256:02769ecf1aadd24cbefe4ac2648dd0d75f80473871e688a9e4c5739ba9229809` | Immutable runtime pin; these harness/eval changes did not rebuild it. |

## Change history

| Date | Repository and commit | Change | Verification and limits |
| --- | --- | --- | --- |
| 2026-09-25 | Eval [`34708e6`](https://github.com/sanafayyaz315/agentic_eval_flow/commit/34708e6649c3f099182c93f644a9ee73c12b3246) | Declared the Flash model's 16,384-token output limit and required a published brief in the rubric. | Source change; the `published_brief` check only verifies a retrieved JSON brief with an `evidenceId`, not full scope or content. |
| 2026-09-25 | Eval [`b5d3e5e`](https://github.com/sanafayyaz315/agentic_eval_flow/commit/b5d3e5e20257c5d7ca73afd48cee571fde2dc764) | Enabled OpenClaw response diagnostics for the briefing. | Source change; see the [Flash diagnostic handoff](morning-briefing-flash-16k-gcp6f-handoff.md) for its live run. |
| 2026-09-28 | Eval [`d8ca0f3`](https://github.com/sanafayyaz315/agentic_eval_flow/commit/d8ca0f30b442bfb29be2a0aa711a19e089c4b10f) | Forwarded a selectable M365 inbox cap through the Pipeline and Evaluate Task. | Later submitted PipelineRuns showed cap values in their immutable parameters; actual collection counts still need case evidence. |
| 2026-09-28 | Eval [`497d339`](https://github.com/sanafayyaz315/agentic_eval_flow/commit/497d339b91f2a39d5741ff200a1f2a988d08ca9a) | Selected the independent morning-only case, excluding `analysis-panel`. | Used by the verified Gateway cap-30 run below. |
| 2026-09-28 | Harness [`42a74c9`](https://github.com/sanafayyaz315/agent-eval-harness/commit/42a74c9c27b4f89230862db381bd5ccb79295f5e) through [`a4be7a7`](https://github.com/sanafayyaz315/agent-eval-harness/commit/a4be7a7bb4e15dec3afd13a9f70ed8fa1aafbffd) | Added the restricted `brief-reader` profile, explicit parent ownership, and an isolated OpenClaw Gateway with a child-write probe for Forge cases. | The cap-30 Gateway probes reached accepted child spawns; early runs did not yet capture a complete parent response. |
| 2026-09-28 | Harness [`4eff08b`](https://github.com/sanafayyaz315/agent-eval-harness/commit/4eff08b5cb61f0c50bc9361be920fdde5b51158f) and [`2cc154c`](https://github.com/sanafayyaz315/agent-eval-harness/commit/2cc154c0f7b7092b11b484dee6b60247be490791) | Added MLflow turn usage and improved Gateway response handling and stable diagnostic downloads. | The earlier raw-stream download race no longer appeared in the later successful Gateway run; artifact contents require separate inspection. |
| 2026-09-28 | Harness [`116498a`](https://github.com/sanafayyaz315/agent-eval-harness/commit/116498a54c39ccd3e75b78262792f40b94066cdf) and [`98366a7`](https://github.com/sanafayyaz315/agent-eval-harness/commit/98366a7193f46292513cd913b0a571a624b70a27) | Kept the Gateway alive through child continuation and waited for the parent's final report after full publication. | `sana-morning-briefing-gateway-30-mrm5b` at `98366a7` produced a full `brief.json`, two child result files with matching evidence ID, and a 4,288-character final response. AEH reward was 0.35 versus 0.5. See the [Gateway handoff](morning-briefing-brief-reader-gateway-handoff.md). |
| 2026-09-28 | Harness [`7ac4356`](https://github.com/sanafayyaz315/agent-eval-harness/commit/7ac43562bf91e9d1afd8bdf3c1abf7f908fca119) | Logged numeric OpenClaw token usage per turn and per case in Evaluate logs. | The cap-50 `sana-morning-briefing-gateway-cap-25wkg` log showed turn 4 at 16,384 output tokens, including 15,740 reasoning tokens, then `stop_reason: error`; this is consistent with output-budget exhaustion, without an explicit provider finish code. |
| 2026-09-28 | Eval [`7a6f498`](https://github.com/sanafayyaz315/agentic_eval_flow/commit/7a6f498b08e9585443b33895ef055ad54d6d299b) | Raised the Flash model's agent-turn `maxTokens` from 16,384 to 128,000. | The cap-100 `sana-morning-briefing-gateway-cap-100-hgjsp` submitted this revision and harness `7ac4356`. A pinned revision proves the configured value, not the provider's accepted maximum or final case outcome. |
| 2026-09-28 | Harness [`adde054`](https://github.com/sanafayyaz315/agent-eval-harness/commit/adde05406aaabcd63b1bfe6eecd93fd564973265) | Made the separate LLM preflight request configurable with `runner.settings.llm_preflight_max_tokens`; default remains 512. | 74 focused OpenShell tests and pre-commit passed. This is on a new branch and did not change the harness revision used by the cap-100 run above. |
| 2026-09-28 | Eval [`2194681`](https://github.com/sanafayyaz315/agentic_eval_flow/commit/219468160921758740e9eadcc8a904029808e504) | Declared `runner.settings.llm_preflight_max_tokens: 512` in `eval.yaml`. | The new [shareable Gateway template](../pipeline/runs/morning-briefing-gateway-template.yaml) pins this eval commit and the `adde054` harness branch. YAML parsing and OpenShift server-side dry run passed; no live PipelineRun at these combined pins is recorded here. |

## Add the next entry

Record the date, repository and full commit, changed behavior, tests, and any
PipelineRun that resolved that commit. Keep code/config verification separate
from agent completion, published `brief.json` scope, judge score, and final
PipelineRun condition. Do not treat a local uncommitted YAML or a branch name
as an immutable evaluation revision.
