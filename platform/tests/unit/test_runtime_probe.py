from types import SimpleNamespace

import pytest
from probe_serverless_runtime import job_arguments, select_successful_task


def task(key, state):
    return SimpleNamespace(
        task_key=key, state=SimpleNamespace(result_state=SimpleNamespace(value=state))
    )


def test_duplicate_failure_attempt_does_not_hide_successful_delta_task():
    successful = task("delta_replay", "SUCCESS")
    assert (
        select_successful_task(
            [
                task("expected_failure", "FAILED"),
                successful,
                task("expected_failure", "TIMEDOUT"),
            ],
            "delta_replay",
        )
        is successful
    )
    with pytest.raises(AssertionError):
        select_successful_task([task("delta_replay", "PENDING")], "delta_replay")


def test_runtime_fixture_has_bounded_environment_and_no_notifications():
    args = job_arguments("/Workspace/hcp/probes/fixture.whl")
    assert args["environments"][0].spec.environment_version == "5"
    assert args["max_concurrent_runs"] == 1 and args["timeout_seconds"] <= 900
    assert "schedule" not in args and "webhook_notifications" not in args
    assert all(
        task.new_cluster is None and task.max_retries == 0 for task in args["tasks"]
    )
