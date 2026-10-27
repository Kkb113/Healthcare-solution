"""Security, clock and lifecycle fault tests independent of cloud services."""

import copy
import logging
from datetime import datetime, timedelta, timezone

import pytest
from hcp.auth.query import object_name
from hcp.auth.scope import Binding, Identity, authorize, resolve
from hcp.common.clocks import business_time, local_instant, utc_instant
from hcp.common.config import Target
from hcp.common.logging import event
from hcp.contracts import Citation, Lineage, QualityResult
from hcp.control.state import (
    admission,
    initial_state,
    needs_shutdown,
    open_window,
    register,
    transition,
    validate,
)

NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)
IDENTITY = Identity(
    "807ebfbb-86ca-41a5-87df-d9c348b89f83",
    "00000000-0000-4000-8000-000000000001",
    "probe-client",
)


def binding(**overrides):
    values = {
        "identity": IDENTITY,
        "version": 1,
        "role": "hcp-clinical",
        "facilities": frozenset({"A"}),
        "phi": True,
        "valid_from": NOW - timedelta(hours=1),
        "valid_to": NOW + timedelta(hours=1),
    }
    return Binding(**(values | overrides))


def test_latest_revocation_or_expiry_never_resurrects_older_grant():
    old = binding()
    for latest in [
        binding(version=2, revoked_at=NOW),
        binding(
            version=2,
            valid_from=NOW - timedelta(hours=2),
            valid_to=NOW - timedelta(minutes=1),
        ),
    ]:
        with pytest.raises(PermissionError, match="INACTIVE"):
            resolve(IDENTITY, [old, latest], NOW)


def test_ambiguity_unmapped_wrong_identity_fail_closed():
    with pytest.raises(PermissionError, match="AMBIGUOUS"):
        resolve(IDENTITY, [binding(), binding()], NOW)
    with pytest.raises(PermissionError, match="UNMAPPED"):
        resolve(IDENTITY, [], NOW)
    other = Identity(
        IDENTITY.tenant_id, "00000000-0000-4000-8000-000000000002", "probe-client"
    )
    with pytest.raises(PermissionError, match="UNMAPPED"):
        resolve(other, [binding()], NOW)


@pytest.mark.parametrize(
    "role,domain,phi,allowed",
    [
        ("hcp-clinical", "clinical", True, True),
        ("hcp-clinical", "finance", False, False),
        ("hcp-finance", "finance", False, True),
        ("hcp-finance", "clinical", False, False),
        ("hcp-operations", "flow", False, True),
        ("hcp-operations", "finance", False, False),
        ("hcp-analysts", "clinical", True, False),
        ("unknown", "flow", False, False),
    ],
)
def test_facility_domain_and_phi_boundaries(role, domain, phi, allowed):
    scope = binding(role=role, phi=role == "hcp-clinical")
    if allowed:
        authorize(scope, "A", domain, phi)
    else:
        with pytest.raises(PermissionError):
            authorize(scope, "A", domain, phi)
    with pytest.raises(PermissionError):
        authorize(scope, "B", domain, False)


def test_binding_validity_is_half_open():
    scope = binding(valid_from=NOW, valid_to=NOW + timedelta(minutes=1))
    assert resolve(IDENTITY, [scope], NOW) == scope
    with pytest.raises(PermissionError):
        resolve(IDENTITY, [scope], scope.valid_to)


def test_dst_fold_and_gap_and_aware_clock_contract():
    with pytest.raises(ValueError, match="Nonexistent"):
        local_instant(datetime(2024, 3, 10, 2, 30))
    with pytest.raises(ValueError, match="Ambiguous"):
        local_instant(datetime(2024, 11, 3, 1, 30))
    assert local_instant(datetime(2024, 11, 3, 1, 30), 1) - local_instant(
        datetime(2024, 11, 3, 1, 30), 0
    ) == timedelta(hours=1)
    assert business_time(NOW).tzinfo.key == "America/Chicago"
    with pytest.raises(ValueError):
        utc_instant(datetime(2024, 1, 1))


@pytest.mark.parametrize("bad", ["hc_dev;DROP", "other", "hc_dev.foo", "HC_DEV"])
def test_sql_identifiers_cannot_escape_target(bad):
    with pytest.raises(ValueError):
        object_name(bad, "gold", "fixture")


def test_explicit_target_and_payload_free_logs(caplog):
    assert Target("test", "warehouse").catalog == "hc_test"
    with pytest.raises(ValueError):
        Target("test", "warehouse", host="https://attacker.invalid")
    with pytest.raises(ValueError):
        event(logging.getLogger("hcp"), "test", access_token="sensitive")
    with caplog.at_level(logging.INFO):
        event(logging.getLogger("hcp"), "complete", row_count=2, status="PASS")
    assert '"row_count": 2' in caplog.text


def test_lineage_quality_and_citation_contracts():
    Lineage("delivery", "source", "a" * 64, "EHR", "1", "batch")
    QualityResult("DQ001", 100, 0)
    Citation("evidence", "v1.1.0", "hc_test.gold.fixture", 1, "a" * 64)
    with pytest.raises(ValueError):
        QualityResult("DQ001", 2, 3)
    with pytest.raises(ValueError):
        Lineage("delivery", "source", "g" * 64, "EHR", "1", "batch")


def awake():
    state = open_window(
        initial_state(), "session", "reservation", NOW + timedelta(minutes=30), NOW
    )
    return transition(state, "AWAKE", ready=True, at=NOW)


def test_sleep_wake_deadline_and_restart_keep_session():
    state = awake()
    admission(state, True, NOW)
    recovered = copy.deepcopy(state)
    with pytest.raises(PermissionError):
        admission(recovered, True, NOW + timedelta(minutes=30))
    assert needs_shutdown(recovered, ["running"], NOW + timedelta(minutes=30))
    stopping = transition(state, "STOPPING")
    with pytest.raises(ValueError):
        transition(stopping, "ASLEEP")
    asleep = transition(stopping, "ASLEEP", asleep=True)
    assert (
        asleep["last_session"]["reservation_id"] == "reservation"
        and asleep["session"] is None
    )


def test_unavailable_budget_unknown_state_and_overlong_window():
    with pytest.raises(PermissionError):
        admission(awake(), False, NOW)
    with pytest.raises(ValueError):
        open_window(
            initial_state(), "session", "reservation", NOW + timedelta(minutes=121), NOW
        )
    state = initial_state() | {"state": "UNKNOWN"}
    with pytest.raises(ValueError):
        validate(state)


def test_manifest_identity_owner_and_idempotency():
    resource = {
        "kind": "warehouse",
        "id": "warehouse",
        "name": "hcp-sql-shared",
        "owner": "terraform",
    }
    state = register(initial_state(), resource)
    assert register(state, resource) == state
    with pytest.raises(ValueError):
        register(state, resource | {"owner": "bundle"})
    with pytest.raises(ValueError):
        register(initial_state(), resource | {"name": "retail"})
    with pytest.raises(ValueError):
        register(initial_state(), resource | {"kind": "unknown"})
    assert needs_shutdown(state, [resource], NOW)
    assert not needs_shutdown(state, [], NOW)


def test_concurrent_wake_is_not_a_second_funded_session():
    state = awake()
    with pytest.raises(ValueError):
        open_window(
            state, "second", "new-reservation", NOW + timedelta(minutes=10), NOW
        )
    with pytest.raises(ValueError):
        transition(state, "ASLEEP", asleep=True)
