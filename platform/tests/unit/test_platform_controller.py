"""Lease/CAS faults and metadata-only emergency shutdown behavior."""

import json

import pytest
from foundation_support import CloudHttpError
from hcp.control.state import initial_state
from platform_control import ControlStore, guard, shutdown


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
    with pytest.raises(ConnectionError):
        guard(BrokenStore(), Client())
    assert Client.warehouses.stopped == ["owned"]


def test_shutdown_refuses_unsupported_owner_adapter():
    with pytest.raises(ValueError, match="adapter"):
        shutdown(object(), [{"kind": "search", "id": "fixture", "running": True}])
