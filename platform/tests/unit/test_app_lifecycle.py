from types import SimpleNamespace

import pytest
from app_lifecycle import wait_initial_provisioning


def record(state, identity=None):
    return SimpleNamespace(
        service_principal_id=identity,
        compute_status=SimpleNamespace(state=SimpleNamespace(value=state)),
    )


def test_no_compute_initial_starting_is_not_started_again():
    pending = iter([record("STARTING"), record("STARTING", 42), record("STOPPED", 42)])
    client = SimpleNamespace(apps=SimpleNamespace(get=lambda name: next(pending)))
    result = wait_initial_provisioning(
        client, "fixture", 100, sleeper=lambda seconds: None, clock=lambda: 0
    )
    assert result.service_principal_id == 42
    assert result.compute_status.state.value == "STOPPED"


def test_initial_provisioning_timeout_is_not_false_readiness():
    client = SimpleNamespace(apps=SimpleNamespace(get=lambda name: record("STARTING")))
    with pytest.raises(TimeoutError):
        wait_initial_provisioning(client, "fixture", 0, clock=lambda: 1)
