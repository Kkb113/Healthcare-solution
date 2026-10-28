"""Lease/CAS faults and metadata-only emergency shutdown behavior."""

import json
from types import SimpleNamespace

import pytest
from foundation_support import CloudHttpError
from hcp.control.state import initial_state
from platform_control import (
    ControlStore,
    RefreshingAzureRest,
    down,
    guard,
    inventory,
    shutdown,
    watch_window,
)


@pytest.fixture(autouse=True)
def isolate_azure_metadata(monkeypatch):
    monkeypatch.setattr("azure_search_lifecycle.inspect_resources", list)


class BlobFixture:
    def __init__(self, fail_write=False):
        self.value = initial_state()
        self.calls = []
        self.fail_write = fail_write

    def request(self, method, url, *, headers=None, body=None):
        self.calls.append((method, url, headers))
        if "?comp=lease" in url:
            return 201, {"x-ms-lease-id": "lease-fixture"}, b""
        if method == "GET":
            return 200, {"ETag": '"revision-zero"'}, json.dumps(self.value).encode()
        assert headers["If-Match"] == '"revision-zero"'
        assert headers["x-ms-lease-id"] == "lease-fixture"
        if self.fail_write:
            raise CloudHttpError(412, "ConditionNotMet")
        self.value = body
        return 201, {}, b""


def test_transaction_uses_lease_and_cas_and_releases_after_stale_write():
    client = BlobFixture(fail_write=True)
    store = ControlStore(client)
    with pytest.raises(CloudHttpError):
        store.transact(lambda old: old | {"state": "FAILED"})
    assert client.value == initial_state()
    assert client.calls[-1][2]["x-ms-lease-action"] == "release"


def test_transaction_records_monotonic_revision():
    client = BlobFixture()
    result = ControlStore(client).transact(lambda old: old | {"state": "FAILED"})
    assert result["revision"] == 1
    assert result["state"] == "FAILED"
    assert client.calls[-1][2]["x-ms-lease-action"] == "release"


def test_explicit_busy_lease_is_retried_but_transaction_runs_once(monkeypatch):
    class BusyLease(BlobFixture):
        attempts = 0

        def request(self, method, url, **kwargs):
            if (
                "?comp=lease" in url
                and kwargs["headers"]["x-ms-lease-action"] == "acquire"
            ):
                self.attempts += 1
                if self.attempts <= 2:
                    raise CloudHttpError(409, "LeaseAlreadyPresent")
            return super().request(method, url, **kwargs)

    delays, mutations = [], []
    monkeypatch.setattr("platform_control.time.sleep", delays.append)

    def mutate(old):
        mutations.append(1)
        return old | {"state": "FAILED"}

    client = BusyLease()
    assert ControlStore(client).transact(mutate)["state"] == "FAILED"
    assert delays == [1, 2] and len(mutations) == 1 and client.attempts == 3


def test_expired_watcher_does_not_stop_a_new_window(monkeypatch):
    state = {
        "state": "AWAKE",
        "session": {"id": "old", "deadline_utc": "2099-01-01T00:00:00Z"},
    }
    store = SimpleNamespace(read=lambda: (state.copy(), "etag"))
    clock = iter([0, 0, 61])
    monkeypatch.setattr("platform_control.time.monotonic", lambda: next(clock))
    monkeypatch.setattr("platform_control.guard", lambda *_: {"status": "PASS"})
    monkeypatch.setattr(
        "platform_control.time.sleep", lambda _: state.update(session={"id": "new"})
    )
    # Final down must check ownership before inventory or a cloud mutation.
    monkeypatch.setattr(
        "platform_control.inventory",
        lambda *_: pytest.fail("stale watcher inspected new resources"),
    )
    assert watch_window(store, object(), 1)["status"] == "SUPERSEDED"


def test_shutdown_rechecks_session_under_lease_before_mutation(monkeypatch):
    initial = {"state": "AWAKE", "session": {"id": "old"}, "resources": []}
    replaced = initial | {"session": {"id": "new"}}
    store = SimpleNamespace(
        read=lambda: (initial, "etag"), transact=lambda mutate: mutate(replaced)
    )
    monkeypatch.setattr("platform_control.inventory", lambda *_: [])
    monkeypatch.setattr(
        "platform_control.shutdown", lambda *_: pytest.fail("new session was stopped")
    )
    assert down(store, object(), expected_session_id="old")["status"] == "SUPERSEDED"


def test_unavailable_control_store_stops_known_compute_without_starting(monkeypatch):
    class BrokenStore:
        def read(self):
            raise ConnectionError("fixture storage unavailable")

    class Warehouse:
        def __init__(self):
            self.stopped = []

        def stop(self, identity):
            self.stopped.append(identity)

    class Client:
        warehouses = Warehouse()

    monkeypatch.setattr(
        "platform_control.inventory",
        lambda client: [
            {"kind": "warehouse", "id": "owned", "running": True, "owned": True},
            {"kind": "warehouse", "id": "unrelated", "running": True, "owned": False},
        ],
    )
    monkeypatch.setattr(
        "lakebase_lifecycle.inspect_resources", lambda client, registered: ([], set())
    )
    with pytest.raises(ConnectionError):
        guard(BrokenStore(), Client())
    assert Client.warehouses.stopped == ["owned"]


def test_shutdown_refuses_unsupported_owner_adapter():
    with pytest.raises(ValueError, match="adapter"):
        shutdown(object(), [{"kind": "unknown", "id": "fixture", "running": True}])


def test_search_failure_does_not_prevent_warehouse_shutdown(monkeypatch):
    stopped = []
    client = SimpleNamespace(warehouses=SimpleNamespace(stop=stopped.append))

    def broken(*_):
        raise CloudHttpError(503, "Unavailable")

    monkeypatch.setattr("azure_search_lifecycle.delete_service", broken)
    with pytest.raises(ValueError, match="adapter shutdown failed"):
        shutdown(
            client,
            [
                {"kind": "azure_search", "id": "fixture", "running": True},
                {"kind": "warehouse", "id": "owned", "running": True},
            ],
        )
    assert stopped == ["owned"]


def test_explicit_401_refreshes_once_but_ambiguous_write_is_not_retried(monkeypatch):
    calls = []

    def expired(self, method, url, **kwargs):
        calls.append(self._token)
        if len(calls) == 1:
            raise CloudHttpError(401, "InvalidAuthenticationInfo")
        return 200, {}, b"ok"

    monkeypatch.setattr("platform_control.AzureRest.request", expired)
    client = object.__new__(RefreshingAzureRest)
    client._token = "expired-fixture"
    assert client.request("PUT", "https://fixture.invalid")[0] == 200
    assert calls == ["expired-fixture", None]

    def ambiguous(self, method, url, **kwargs):
        calls.append(None)
        raise CloudHttpError(503, "ServiceUnavailable")

    monkeypatch.setattr("platform_control.AzureRest.request", ambiguous)
    calls.clear()
    with pytest.raises(CloudHttpError):
        client.request("PUT", "https://fixture.invalid")
    assert len(calls) == 1


def test_job_inventory_uses_supported_pagination_and_does_not_run_jobs():
    settings = SimpleNamespace(
        name="hcp-test-foundation-smoke", schedule=None, trigger=None, continuous=None
    )
    calls = []

    def list_runs(**kwargs):
        calls.append(kwargs)
        assert kwargs["limit"] <= 26
        return []

    client = SimpleNamespace(
        warehouses=SimpleNamespace(list=list),
        jobs=SimpleNamespace(
            list=lambda **kwargs: [SimpleNamespace(job_id=1, settings=settings)],
            get=lambda identity: SimpleNamespace(settings=settings),
            list_runs=list_runs,
        ),
        pipelines=SimpleNamespace(list_pipelines=list),
        apps=SimpleNamespace(list=list),
        serving_endpoints=SimpleNamespace(list=list),
        clusters=SimpleNamespace(list=list),
        vector_search_endpoints=SimpleNamespace(list_endpoints=list),
    )
    result = inventory(client)
    assert len(result) == 1 and result[0]["running"] is False
    assert calls == [{"job_id": 1, "active_only": True, "limit": 25}]


def test_unknown_app_state_and_unmanaged_pipeline_prevent_false_sleep():
    client = SimpleNamespace(
        warehouses=SimpleNamespace(list=list),
        jobs=SimpleNamespace(list=lambda **kwargs: []),
        pipelines=SimpleNamespace(
            list_pipelines=lambda: [
                SimpleNamespace(name="unmanaged", pipeline_id="other")
            ],
            get=lambda identity: SimpleNamespace(state=None),
        ),
        apps=SimpleNamespace(
            list=lambda: [
                SimpleNamespace(name="hcp-foundation-fixture", compute_status=None)
            ]
        ),
        serving_endpoints=SimpleNamespace(list=list),
        clusters=SimpleNamespace(list=list),
        vector_search_endpoints=SimpleNamespace(list_endpoints=list),
    )
    result = inventory(client)
    assert len(result) == 2
    assert all(item["running"] for item in result)
    assert result[0]["owned"] is False
    assert result[1]["owned"] is True
