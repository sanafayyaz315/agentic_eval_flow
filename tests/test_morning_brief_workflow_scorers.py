"""The workflow checks distinguish script calls from the final brief artifact."""

import json
from pathlib import Path

import yaml


EVAL = Path(__file__).resolve().parents[1] / "submissions/openclaw-forge/eval.yaml"
CHECKS = (
    "sealed_brief_evidence",
    "reviewed_brief_batches",
    "composed_full_brief",
    "called_brief_publisher",
    "full_brief_stage_order",
)


def _check(name, outputs):
    judge = next(
        j for j in yaml.safe_load(EVAL.read_text())["judges"] if j["name"] == name
    )
    namespace = {}
    source = "def check(outputs, arguments):\n" + "".join(
        "    " + line + "\n" for line in judge["check"].splitlines()
    )
    exec(compile(source, f"<{name}>", "exec"), namespace)
    return namespace["check"](outputs, {})


def _event(tool_id, name, args):
    return {"type": "assistant", "tools": [{"id": tool_id, "name": name, "input": args}]}


def _result(tool_id, name, result):
    return {"type": "tool_result", "tool_use_id": tool_id, "tool_name": name,
            "is_error": False, "result": result}


def _record():
    evidence_id = "evidence-1"
    evidence = {"evidenceId": evidence_id, "sealed": True, "batches": [{
        "id": "batch-1", "path": ".openclaw/tmp/batches/batch-1.json",
    }]}
    return {
        "files": {
            "brief.json/brief.json": json.dumps({"scope": "full", "evidenceId": evidence_id}),
            ".openclaw/tmp/brief.evidence.json/brief.evidence.json": json.dumps(evidence),
            ".openclaw/tmp/brief.index.json/brief.index.json": json.dumps({
                "evidenceId": evidence_id,
            }),
        },
        "events": [
            _event("sweep", "exec", {"command": "node tools/collect-brief-evidence.mjs"}),
            _result("sweep", "exec", "[diagnostic output redacted]"),
            _event("seal", "exec", {"command": "node tools/collect-brief-evidence.mjs seal"}),
            _result("seal", "exec", "[diagnostic output redacted]"),
            _event("spawn", "sessions_spawn", {
                "agentId": "brief-reader", "lightContext": True,
                "task": "Read .openclaw/tmp/batches/batch-1.json",
            }),
            _result("spawn", "sessions_spawn", json.dumps({"status": "accepted"})),
            _event("yield", "sessions_yield", {}),
            _event("read", "read", {"path": "$WORKSPACE_DIR/.openclaw/tmp/batches/batch-1.result.json"}),
            _result("read", "read", json.dumps({
                "batchId": "batch-1", "evidenceId": evidence_id,
            })),
            _event("compose", "exec", {
                "command": "node tools/compose-brief.mjs .openclaw/tmp/items-full.json",
            }),
            _result("compose", "exec", "composed full brief candidate for evidence " + evidence_id),
            _event("publish", "exec", {"command": "node tools/publish-brief.mjs"}),
            _result("publish", "exec", "[diagnostic output redacted]"),
        ],
    }


def test_all_workflow_stages_are_observed():
    record = _record()
    assert all(_check(name, record) is True for name in CHECKS)
    judges = yaml.safe_load(EVAL.read_text())["judges"]
    assert all(next(j for j in judges if j["name"] == name)["if"] ==
               "annotations.get('requires_published_brief')" for name in CHECKS)


def test_seal_requires_call_and_sealed_artifact():
    record = _record()
    record["events"] = [e for e in record["events"] if e.get("tool_use_id") != "seal"]
    record["events"] = [e for e in record["events"] if not any(
        t.get("id") == "seal" for t in e.get("tools") or [])]
    assert _check("sealed_brief_evidence", record) is False

    record = _record()
    key = ".openclaw/tmp/brief.evidence.json/brief.evidence.json"
    evidence = json.loads(record["files"][key])
    evidence["sealed"] = False
    record["files"][key] = json.dumps(evidence)
    assert _check("sealed_brief_evidence", record) is False


def test_every_declared_batch_needs_spawn_and_matching_readback():
    record = _record()
    assert _check("reviewed_brief_batches", record) is True
    record["events"][4]["tools"][0]["input"]["agentId"] = "other"
    assert _check("reviewed_brief_batches", record) is False

    record = _record()
    record["events"][8]["result"] = json.dumps({
        "batchId": "batch-1", "evidenceId": "old-evidence",
    })
    assert _check("reviewed_brief_batches", record) is False


def test_composition_needs_success_message_for_published_evidence():
    record = _record()
    record["events"][10]["result"] = "the brief was not composed (Command exited with code 1)"
    assert _check("composed_full_brief", record) is False


def test_publisher_invocation_is_distinct_from_publication_result():
    record = _record()
    record["events"] = record["events"][:-2]
    assert _check("called_brief_publisher", record) is False
    record = _record()
    record["events"][10]["result"] = "composed attention brief candidate for evidence evidence-1"
    assert _check("called_brief_publisher", record) is False
    # Its output can be redacted. The separate published_brief scorer checks
    # the final artifact and must not infer success from this result alone.
    assert _check("called_brief_publisher", _record()) is True


def test_full_run_stage_order_rejects_early_publication():
    record = _record()
    assert _check("full_brief_stage_order", record) is True
    record["events"] = record["events"][:2] + record["events"][9:] + record["events"][2:9]
    assert _check("full_brief_stage_order", record) is False
