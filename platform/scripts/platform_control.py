"""External control-plane sleep/wake/guard; never runs SQL or a Databricks job."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "platform/src"))

from foundation_ledger import BlobLedger, exposure, reserve
from foundation_support import CONFIG, AzureRest, CloudHttpError, load, now, save
from hcp.control.funding import claim
from hcp.control.state import (
    admission,
    initial_state,
    instant,
    needs_shutdown,
    open_window,
    register,
    transition,
    validate,
)

SETTINGS = ROOT / "platform/config/platform-foundation.json"
OUTPUT = ROOT / "output/platform-foundation"


def has_funding(ledger):
    settings = load(SETTINGS)
    required = {
        settings["probe_reservation_id"]: settings["new_probe_reservation_paise"]
    }
    if settings.get("contingency_reservation_id"):
        amendment = load(ROOT / settings["cost_amendment"])
        if amendment["status"] != "APPROVED":
            return False
        required[settings["contingency_reservation_id"]] = settings[
            "contingency_reservation_paise"
        ]
    return not exposure(ledger)["pause_new_work"] and all(
        ledger["reservations"].get(key, {}).get("paise", 0) >= amount
        for key, amount in required.items()
    )


def admit_operation(store, operation_id, meter, units):
    def action(value):
        admission(value, has_funding(BlobLedger().read()[0]))
        return claim(value, operation_id, meter, units)

    return store.transact(action)


class RefreshingAzureRest(AzureRest):
    """Refresh once after an explicit authentication rejection, including writes.

    An HTTP 401 means the service rejected authentication before mutation. Other
    ambiguous write failures remain uncertain and are never blindly retried.
    """

    def request(self, method, url, **kwargs):
        try:
            return super().request(method, url, **kwargs)
        except CloudHttpError as error:
            if error.status != 401:
                raise
            self._token = None
            return super().request(method, url, **kwargs)


def workspace_client():
    from databricks.sdk import WorkspaceClient

    target = load(ROOT / "platform/config/workspace.json")
    os.environ["ARM_SUBSCRIPTION_ID"] = target["subscription_id"]
    if os.environ.get("DATABRICKS_HOST"):
        if os.environ["DATABRICKS_HOST"].rstrip("/") != target["workspace_host"]:
            raise ValueError("Wrong workspace environment")
        return WorkspaceClient()
    return WorkspaceClient(profile=target["workspace_profile"])


class ControlStore:
    def __init__(self, client=None):
        config = load(CONFIG)
        self.settings = load(SETTINGS)
        host = config["storage_account"] + ".blob.core.windows.net"
        self.client = client or RefreshingAzureRest(
            config["workspace_subscription"], "https://storage.azure.com/", {host}
        )
        self.url = f"https://{host}/control/{self.settings['control_blob']}"

    @staticmethod
    def headers(extra=None):
        return BlobLedger.headers(extra)

    def initialize(self):
        value = initial_state()
        try:
            self.client.request(
                "PUT",
                self.url,
                body=value,
                headers=self.headers(
                    {"x-ms-blob-type": "BlockBlob", "If-None-Match": "*"}
                ),
            )
        except CloudHttpError as error:
            if error.status != 412 and not (
                error.status == 409 and error.code == "BlobAlreadyExists"
            ):
                raise
        return self.read()[0]

    def read(self):
        _, headers, raw = self.client.request("GET", self.url, headers=self.headers())
        value = json.loads(raw)
        validate(value)
        etag = headers.get("ETag") or headers.get("Etag")
        if not etag:
            raise ValueError("Control ETag missing; fail closed")
        return value, etag

    def transact(self, action):
        for attempt in range(4):
            try:
                _, headers, _ = self.client.request(
                    "PUT",
                    self.url + "?comp=lease",
                    headers=self.headers(
                        {"x-ms-lease-action": "acquire", "x-ms-lease-duration": "60"}
                    ),
                )
                break
            except CloudHttpError as error:
                if (
                    error.status != 409
                    or error.code != "LeaseAlreadyPresent"
                    or attempt == 3
                ):
                    raise
                # Explicit rejected acquisition made no mutation. Never retry
                # an ambiguous write or stale CAS under this policy.
                time.sleep(attempt + 1)
        lease = headers.get("x-ms-lease-id")
        if not lease:
            raise ValueError("Control lease missing; fail closed")
        try:
            previous, etag = self.read()
            changed = action(copy.deepcopy(previous))
            validate(changed)
            if changed == previous:
                return previous
            changed["revision"] = previous["revision"] + 1
            changed["updated_at"] = now()
            events = list(previous.get("events", []))
            if len(events) >= 10000:
                raise PermissionError(
                    "Archive control audit history before another mutation"
                )
            events.append(
                {
                    "revision": changed["revision"],
                    "at": changed["updated_at"],
                    "from": previous["state"],
                    "to": changed["state"],
                    "session_id": changed["session"]["id"]
                    if changed.get("session")
                    else None,
                    "resource_count": len(changed["resources"]),
                    "cost_claim_count": len(changed.get("cost_claims", {})),
                }
            )
            changed["events"] = events
            self.client.request(
                "PUT",
                self.url,
                body=changed,
                headers=self.headers(
                    {
                        "If-Match": etag,
                        "x-ms-lease-id": lease,
                        "x-ms-blob-type": "BlockBlob",
                    }
                ),
            )
            return changed
        finally:
            self.client.request(
                "PUT",
                self.url + "?comp=lease",
                headers=self.headers(
                    {"x-ms-lease-action": "release", "x-ms-lease-id": lease}
                ),
            )


def owned_name(name):
    return name == load(SETTINGS)["warehouse"]["name"] or name.startswith(
        ("hcp-foundation-", "hcp-dev-", "hcp-test-")
    )


def inventory(client, registered=()):
    """Metadata APIs only. Existing unrelated and system foundation endpoints excluded."""
    warehouses = [
        {
            "kind": "warehouse",
            "id": w.id,
            "name": w.name,
            "state": w.state.value,
            "running": w.state.value != "STOPPED",
            "owner": "terraform",
            "owned": owned_name(w.name),
        }
        for w in client.warehouses.list()
    ]
    jobs = []
    for job in client.jobs.list(expand_tasks=False):
        settings = client.jobs.get(job.job_id).settings
        scheduled = (
            bool(settings.schedule and settings.schedule.pause_status.value != "PAUSED")
            or bool(
                settings.trigger and settings.trigger.pause_status.value != "PAUSED"
            )
            or bool(
                settings.continuous
                and settings.continuous.pause_status.value != "PAUSED"
            )
        )
        runs = list(
            client.jobs.list_runs(job_id=job.job_id, active_only=True, limit=25)
        )
        jobs.append(
            {
                "kind": "job",
                "id": str(job.job_id),
                "name": settings.name,
                "running": bool(runs) or scheduled,
                "active_run_ids": [r.run_id for r in runs],
                "unpaused_trigger": scheduled,
                "owner": "bundle",
                "owned": owned_name(settings.name),
            }
        )
    from lakebase_lifecycle import inspect_resources

    lakebase, sync_pipeline_ids = inspect_resources(client, registered)
    pipelines = []
    for pipeline in client.pipelines.list_pipelines():
        record = client.pipelines.get(pipeline.pipeline_id)
        state = record.state.value if record.state else "UNKNOWN"
        pipelines.append(
            {
                "kind": "pipeline",
                "id": pipeline.pipeline_id,
                "name": pipeline.name,
                "running": state not in {"IDLE", "DELETED", "FAILED"},
                "state": state,
                "owned": owned_name(pipeline.name)
                or pipeline.pipeline_id in sync_pipeline_ids,
                "owner": "bundle",
            }
        )
    apps = [
        {
            "kind": "app",
            "id": app.name,
            "name": app.name,
            "running": not app.compute_status
            or app.compute_status.state.value != "STOPPED",
            "state": app.compute_status.state.value
            if app.compute_status
            else "UNKNOWN",
            "owner": "bundle",
            "owned": owned_name(app.name),
        }
        for app in client.apps.list()
    ]
    serving = [
        {
            "kind": "serving",
            "id": endpoint.name,
            "name": endpoint.name,
            "running": True,
            "state": endpoint.state.ready.value if endpoint.state else "UNKNOWN",
            "owner": "api-adapter",
        }
        for endpoint in client.serving_endpoints.list()
        if owned_name(endpoint.name)
    ]
    search = [
        {
            "kind": "search",
            "id": endpoint.name,
            "name": endpoint.name,
            "running": True,
            "state": str(endpoint.endpoint_status.state)
            if endpoint.endpoint_status
            else "UNKNOWN",
            "owner": "api-adapter",
            "owned": endpoint.name.startswith("hcp-foundation-"),
        }
        for endpoint in client.vector_search_endpoints.list_endpoints()
    ]
    # Search/Lakebase are registered before their funded probe. The adapters
    # extend this manifest with their API status; unknown status is never sleep.
    clusters = [
        {
            "kind": "classic_cluster",
            "id": c.cluster_id,
            "name": c.cluster_name,
            "running": c.state.value not in {"TERMINATED", "ERROR"},
            "state": c.state.value,
            "owned": False,
            "owner": "unmanaged",
        }
        for c in client.clusters.list()
    ]
    result = (
        warehouses + jobs + pipelines + apps + serving + clusters + search + lakebase
    )
    return result


def shutdown(client, resources):
    from databricks.sdk.service.jobs import JobSettings, PauseStatus

    actions = []
    for resource in sorted(
        resources,
        key=lambda r: {
            "job": 0,
            "pipeline": 1,
            "synced_table": 2,
            "app": 3,
            "serving": 4,
            "lakebase": 5,
            "warehouse": 6,
        }.get(r["kind"], 5),
    ):
        if not resource["running"] or not resource.get("owned", True):
            continue
        kind, identity = resource["kind"], resource["id"]
        if kind == "job":
            job = client.jobs.get(int(identity)).settings
            updates = JobSettings()
            changed = False
            for attr in ["schedule", "trigger", "continuous"]:
                value = getattr(job, attr)
                if value:
                    value.pause_status = PauseStatus.PAUSED
                    setattr(updates, attr, value)
                    changed = True
            if changed:
                client.jobs.update(int(identity), new_settings=updates)
            for run_id in resource["active_run_ids"]:
                client.jobs.cancel_run(run_id)
        elif kind == "pipeline":
            client.pipelines.stop(identity)
        elif kind == "app":
            client.apps.stop(identity)
        elif kind == "serving":
            client.serving_endpoints.delete(identity)
        elif kind == "warehouse":
            client.warehouses.stop(identity)
        elif kind == "search":
            if not identity.startswith("hcp-foundation-"):
                raise PermissionError(
                    "Search deletion requires a tested rebuild/snapshot owner"
                )
            indexes = list(client.vector_search_indexes.list_indexes(identity))
            if any(
                not index.name.startswith("hc_test._foundation_probe.")
                for index in indexes
            ):
                raise PermissionError("Unexpected index on temporary search endpoint")
            for index in indexes:
                client.vector_search_indexes.delete_index(index.name)
            client.vector_search_endpoints.delete_endpoint(identity)
        elif kind == "lakebase":
            from lakebase_lifecycle import hard_disable

            hard_disable(client, identity)
        elif kind == "synced_table":
            from lakebase_lifecycle import remove_temporary_sync

            remove_temporary_sync(client, identity)
        else:
            raise ValueError(
                "Resource owner adapter is not registered; cannot certify sleep"
            )
        actions.append({"kind": kind, "id": identity, "action": "sleep_requested"})
    return actions


_ANY_SESSION = object()


class SupersededSession(RuntimeError):
    """A newer window owns the controller; an old watcher must leave it alone."""


def session_id(state):
    return (state.get("session") or {}).get("id")


def down(store, client, timeout=360, expected_session_id=_ANY_SESSION):
    state, _ = store.read()
    if (
        expected_session_id is not _ANY_SESSION
        and session_id(state) != expected_session_id
    ):
        return {"status": "SUPERSEDED", "actions": [], "metadata_only": True}
    if any(
        r["kind"]
        not in {
            "warehouse",
            "job",
            "pipeline",
            "app",
            "serving",
            "search",
            "lakebase",
            "synced_table",
        }
        for r in state["resources"]
    ):
        raise ValueError(
            "A registered resource needs its inspection/stop adapter; sleep cannot be certified"
        )
    resources = inventory(client, state["resources"])
    if state["state"] == "ASLEEP" and not any(r["running"] for r in resources):
        return {"status": "PASS", "state": "ASLEEP", "running": 0, "actions": []}

    def begin_shutdown(old):
        if (
            expected_session_id is not _ANY_SESSION
            and session_id(old) != expected_session_id
        ):
            raise SupersededSession("Shutdown belongs to a previous window")
        if old["state"] == "ASLEEP":
            old = old | {"state": "FAILED"}
        return transition(old, "STOPPING")

    try:
        store.transact(begin_shutdown)
    except SupersededSession:
        return {"status": "SUPERSEDED", "actions": [], "metadata_only": True}
    try:
        actions = shutdown(client, resources)
    except Exception:
        store.transact(lambda old: transition(old, "FAILED"))
        raise
    if any(r["running"] and not r.get("owned", True) for r in resources):
        store.transact(lambda old: transition(old, "FAILED"))
        raise PermissionError(
            "Unmanaged compute is active; owner intervention required"
        )
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        resources = inventory(client, state["resources"])
        if not any(r["running"] for r in resources):
            store.transact(lambda old: transition(old, "ASLEEP", asleep=True))
            return {
                "status": "PASS",
                "state": "ASLEEP",
                "running": 0,
                "actions": actions,
                "metadata_only": True,
            }
        time.sleep(5)
    store.transact(lambda old: transition(old, "FAILED"))
    raise TimeoutError("Shutdown did not settle; platform remains FAILED")


def guard(store, client):
    try:
        state, _ = store.read()
    except Exception:
        # A missing/corrupt/unavailable lease store must not leave paid resources
        # running. Shutdown uses live metadata and the closed healthcare prefix;
        # it never interprets untrusted state or starts compute for inspection.
        shutdown(client, inventory(client))
        # Fixed emergency scope covers a corrupt/unavailable manifest without
        # querying Postgres or touching an unrelated project. Stop other known
        # compute first even when the Lakebase control API is unavailable.
        from lakebase_lifecycle import PROJECT, SYNC, inspect_resources

        emergency, _ = inspect_resources(
            client,
            [
                {"kind": "lakebase", "id": PROJECT},
                {"kind": "synced_table", "id": SYNC},
            ],
        )
        shutdown(client, emergency)
        raise
    if any(
        r["kind"]
        not in {
            "warehouse",
            "job",
            "pipeline",
            "app",
            "serving",
            "search",
            "lakebase",
            "synced_table",
        }
        for r in state["resources"]
    ):
        raise ValueError("A registered resource cannot yet be inspected; fail closed")
    resources = inventory(client, state["resources"])
    running = [r for r in resources if r["running"]]
    if needs_shutdown(state, running):
        return down(store, client, expected_session_id=session_id(state))
    return {
        "status": "PASS",
        "state": state["state"],
        "running": len(running),
        "metadata_only": True,
        "workloads_launched": 0,
    }


def watch_window(store, client, minutes):
    """Watch exactly the session present at launch, including final cleanup.

    The durable lease/CAS check in down also protects the gap between reading
    the session and requesting a stop. Scheduled one-shot guard remains global.
    """
    owned = session_id(store.read()[0])
    if owned is None:
        return guard(store, client)
    started = time.monotonic()
    while time.monotonic() - started < minutes * 60:
        if session_id(store.read()[0]) != owned:
            return {"status": "SUPERSEDED", "metadata_only": True, "actions": []}
        result = guard(store, client)
        current = store.read()[0]
        if session_id(current) != owned:
            return result
        if instant(current["session"]["deadline_utc"]) <= datetime.now(timezone.utc):
            return down(store, client, expected_session_id=owned)
        time.sleep(30)
    return down(store, client, expected_session_id=owned)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=[
            "initialize",
            "reserve",
            "reserve-contingency",
            "open",
            "up",
            "down",
            "guard",
            "watch",
            "register",
            "claim",
            "status",
        ],
    )
    parser.add_argument("--minutes", type=int, default=60)
    parser.add_argument("--resource-json", type=Path)
    parser.add_argument("--operation-id")
    parser.add_argument("--meter")
    parser.add_argument("--units", type=int)
    args = parser.parse_args()
    settings = load(SETTINGS)
    store = ControlStore()
    client = None
    if args.command == "initialize":
        result = {"status": "PASS", "state": store.initialize()}
    elif args.command == "reserve":
        ledger = BlobLedger().transact(
            lambda value: reserve(
                value,
                settings["probe_reservation_id"],
                settings["new_probe_reservation_paise"],
                2,
            )
        )
        result = {"status": "PASS", "budget": exposure(ledger)}
    elif args.command == "reserve-contingency":
        revision = load(ROOT / settings["cost_amendment"])
        if (
            revision["status"] != "APPROVED"
            or revision["proposed_build_ceiling_inr"] != "20000.00"
        ):
            raise PermissionError("No approved within-ceiling contingency amendment")
        ledger = BlobLedger().transact(
            lambda value: reserve(
                value,
                settings["contingency_reservation_id"],
                settings["contingency_reservation_paise"],
                2,
            )
        )
        result = {
            "status": "PASS",
            "budget": exposure(ledger),
            "amendment": settings["cost_amendment"],
        }
    elif args.command == "open":
        ledger = BlobLedger().read()[0]
        if not has_funding(ledger):
            raise PermissionError("No funded reservation")
        if not 1 <= args.minutes <= settings["window_max_minutes"]:
            raise ValueError("Invalid funded window duration")
        client = workspace_client()
        if any(r["running"] for r in inventory(client, store.read()[0]["resources"])):
            raise PermissionError(
                "Reconcile existing active resources before opening a window"
            )
        result = store.transact(
            lambda value: open_window(
                value,
                uuid.uuid4().hex,
                settings["probe_reservation_id"],
                datetime.now(timezone.utc) + timedelta(minutes=args.minutes),
            )
        )
    elif args.command == "claim":

        def funded_claim(value):
            admission(value, True)
            ledger = BlobLedger().read()[0]
            if not has_funding(ledger):
                raise PermissionError("No funded reservation")
            return claim(value, args.operation_id, args.meter, args.units)

        result = store.transact(funded_claim)
    elif args.command == "register":
        if not args.resource_json:
            parser.error("Resource manifest JSON required")
        result = store.transact(lambda value: register(value, load(args.resource_json)))
    elif args.command == "status":
        result = store.read()[0]
    else:
        client = workspace_client()
        if args.command == "up":
            state = store.read()[0]
            ledger = BlobLedger().read()[0]
            admission(
                state,
                has_funding(ledger),
            )
            declared = [
                r
                for r in state["resources"]
                if r["kind"] == "warehouse"
                and r.get("wake_in_profile") == state["session"]["profile"]
            ]
            if len(declared) > 1:
                raise PermissionError("Only one SQL cluster is funded")
            for resource in declared:
                client.warehouses.start(resource["id"]).result(
                    timeout=timedelta(minutes=8)
                )
                admission(store.read()[0], True)
            result = store.transact(
                lambda value: transition(value, "AWAKE", ready=True)
            )
        elif args.command == "down":
            result = down(store, client)
        elif args.command == "guard":
            result = guard(store, client)
        else:
            result = watch_window(store, client, args.minutes)
    report = {"observed_at": now(), "command": args.command, "result": result}
    save(OUTPUT / ("control-" + args.command + ".json"), report)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
