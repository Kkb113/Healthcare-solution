"""Reconcile retained runtime evidence without rerunning paid workloads.

The original failed harness result is immutable. Successful and expected-failure
task attempts are selected by both key and state, never collapsed by task key.
"""

import hashlib
import json
from datetime import datetime
from itertools import pairwise

from foundation_support import ROOT, load, now, save

OUTPUT = ROOT / "output/platform-foundation"


def reconcile(probe, output, terminal, events):
    run = terminal["run"]
    tasks = run["tasks"]
    successes = [
        t
        for t in tasks
        if t["task_key"] == "delta_replay"
        and t["state"].get("result_state") == "SUCCESS"
    ]
    expected = [
        t
        for t in tasks
        if t["task_key"] == "expected_failure"
        and t["state"].get("result_state") == "FAILED"
    ]
    assert len(successes) == len(expected) == 1
    assert successes[0]["run_id"] == output["metadata"]["run_id"]
    assert output["logs_truncated"] is False
    result = json.loads(output["logs"].strip())
    assert result["status"] == "PASS" and result["rows"] == 3
    assert result["replay_idempotent"] is True
    assert result["append_version"] < result["version"]
    assert result["historical_sentinel_rows"] == 1
    assert (
        probe["job_configuration"]["environments"][0]["spec"]["environment_version"]
        == "5"
    )
    assert probe["pipeline_configuration"]["serverless"] is True
    assert probe["pipeline_configuration"]["channel"] == "CURRENT"
    assert any(
        e["event_type"] == "update_progress" and "COMPLETED" in e["message"]
        for e in events
    )
    assert not probe["notifications_enabled"] and not probe["cleanup_errors"]
    assert all(probe["cleanup"].values())
    samples = probe["samples"]
    times = [datetime.fromisoformat(s["at"]) for s in samples]
    intervals = [(b - a).total_seconds() for a, b in pairwise(times)]
    assert max(intervals) <= 120
    failed = [
        s
        for s in samples
        if s["run_state"].get("result_state") in {"FAILED", "TIMEDOUT"}
    ]
    assert failed
    detected = datetime.fromisoformat(failed[0]["at"])
    total_detection = (
        detected - datetime.fromisoformat(probe["started_at"])
    ).total_seconds()
    assert total_detection <= 900
    return {
        "observed_at": now(),
        "runtime_status": "FUNCTIONAL_PASS_BILLING_PENDING",
        "polling_status": "PASS",
        "original_harness_status": probe["status"],
        "harness_issue": "Task-key dictionary overwrote an earlier FAILED attempt with a retried TIMEDOUT attempt; all task attempts are retained here.",
        "constant_fixture_result": result,
        "task_attempts": [
            {k: t.get(k) for k in ["task_key", "run_id", "attempt_number", "state"]}
            for t in tasks
        ],
        "polling_principal": probe["polling_principal"],
        "poll_samples": len(samples),
        "maximum_observed_poll_interval_seconds": max(intervals),
        "failure_detected_seconds_from_probe_start": total_detection,
        "webhooks_enabled": False,
        "system_tables_required_for_detection": False,
        "cleanup": probe["cleanup"],
        "billing_reservations_released": False,
    }


def main():
    names = [
        "serverless-runtime.json",
        "runtime-success-output.json",
        "runtime-terminal-reconciliation.json",
        "runtime-pipeline-events.json",
    ]
    report = reconcile(*(load(OUTPUT / name) for name in names))
    report["evidence_sha256"] = {
        name: hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest() for name in names
    }
    save(OUTPUT / "runtime-probe-reconciliation.json", report)
    print(
        json.dumps(
            {
                key: report[key]
                for key in [
                    "runtime_status",
                    "polling_status",
                    "poll_samples",
                    "failure_detected_seconds_from_probe_start",
                ]
            }
        )
    )


if __name__ == "__main__":
    main()
