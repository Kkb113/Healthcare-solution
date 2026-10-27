from types import SimpleNamespace

import pytest
from lakebase_lifecycle import (
    PROJECT,
    SYNC,
    hard_disable,
    inspect_resources,
    scoped_endpoint,
    verify_sync_project,
)

ENDPOINT = PROJECT + "/branches/production/endpoints/primary"


def test_unregistered_lakebase_never_opens_postgres_or_queries_data():
    assert inspect_resources(object(), []) == ([], set())


@pytest.mark.parametrize(
    "name",
    [
        "projects/retail/branches/production/endpoints/primary",
        PROJECT,
        ENDPOINT + "/extra",
    ],
)
def test_foreign_or_ambiguous_endpoint_is_rejected_before_mutation(name):
    with pytest.raises(PermissionError):
        scoped_endpoint(name)


def test_suspended_but_not_hard_disabled_endpoint_still_prevents_sleep():
    endpoint = SimpleNamespace(
        name=ENDPOINT,
        status=SimpleNamespace(
            disabled=False, current_state=SimpleNamespace(value="IDLE")
        ),
    )
    client = SimpleNamespace(
        postgres=SimpleNamespace(
            get_project=lambda name: SimpleNamespace(name=PROJECT),
            list_branches=lambda name: [
                SimpleNamespace(name=PROJECT + "/branches/production")
            ],
            list_endpoints=lambda name: [endpoint],
        )
    )
    records, _ = inspect_resources(client, [{"kind": "lakebase", "id": PROJECT}])
    assert records[0]["running"] is True
    endpoint.status.disabled = True
    records, _ = inspect_resources(client, [{"kind": "lakebase", "id": PROJECT}])
    assert records[0]["running"] is False


def test_hard_disable_has_exact_mask_bounded_wait_and_readback():
    calls = []
    operation = SimpleNamespace(
        wait=lambda options: calls.append(
            ("wait_seconds", options.timeout.total_seconds())
        )
    )

    def update(name, value, mask):
        calls.append((name, value.spec.disabled, mask.ToJsonString()))
        return operation

    client = SimpleNamespace(
        postgres=SimpleNamespace(
            update_endpoint=update,
            get_endpoint=lambda name: SimpleNamespace(
                status=SimpleNamespace(disabled=True)
            ),
        )
    )
    hard_disable(client, ENDPOINT)
    assert calls == [(ENDPOINT, True, "spec.disabled"), ("wait_seconds", 90)]


def test_synced_table_must_match_its_declared_project():
    with pytest.raises(PermissionError):
        verify_sync_project(
            SimpleNamespace(
                spec=SimpleNamespace(branch="projects/retail/branches/production")
            )
        )


def test_guard_never_uses_synced_table_api_that_connects_to_disabled_postgres():
    endpoint = SimpleNamespace(
        name=ENDPOINT,
        status=SimpleNamespace(
            disabled=True, current_state=SimpleNamespace(value="IDLE")
        ),
    )
    client = SimpleNamespace(
        postgres=SimpleNamespace(
            get_project=lambda _: SimpleNamespace(name=PROJECT),
            list_branches=lambda _: [
                SimpleNamespace(name=PROJECT + "/branches/production")
            ],
            list_endpoints=lambda _: [endpoint],
            get_synced_table=lambda _: pytest.fail(
                "GetSyncedTable must not be a sleep check"
            ),
        ),
        pipelines=SimpleNamespace(list_pipelines=list),
    )
    records, pipeline_ids = inspect_resources(
        client, [{"kind": "synced_table", "id": SYNC}]
    )
    assert not pipeline_ids and all(not r["running"] for r in records)


def test_status_only_ga_readback_is_scoped_without_assuming_missing_spec():
    verify_sync_project(
        SimpleNamespace(spec=None, status=SimpleNamespace(project=PROJECT))
    )
    for status in [
        None,
        SimpleNamespace(project=None),
        SimpleNamespace(project="projects/retail"),
    ]:
        with pytest.raises(PermissionError):
            verify_sync_project(SimpleNamespace(spec=None, status=status))
    with pytest.raises(PermissionError):
        verify_sync_project(
            SimpleNamespace(
                spec=SimpleNamespace(branch=PROJECT + "/branches/production"),
                status=SimpleNamespace(project="projects/retail"),
            )
        )
