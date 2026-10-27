"""One fixed SELECT, then metadata-only auto-stop observation. Never wakes to poll."""

import time
from datetime import datetime, timezone

from deploy_security_baseline import execute
from foundation_support import ROOT, now, save
from platform_control import ControlStore, instant, workspace_client


def main():
    client = workspace_client()
    identity = "bd30bdac29080126"
    warehouse = client.warehouses.get(identity)
    assert warehouse.enable_serverless_compute is True
    assert warehouse.cluster_size == "2X-Small"
    assert warehouse.min_num_clusters == warehouse.max_num_clusters == 1
    assert warehouse.auto_stop_mins == 5
    state = ControlStore().read()[0]
    if (
        instant(state["session"]["deadline_utc"]) - datetime.now(timezone.utc)
    ).total_seconds() < 420:
        raise PermissionError(
            "At least seven funded minutes required to exclude hard-stop interference"
        )
    response = execute(client, identity, "SELECT 1 AS fixture")
    assert response.result.data_array == [["1"]]
    last_query_completed = datetime.now(timezone.utc)
    start = time.monotonic()
    samples = []
    while time.monotonic() - start < 360:
        observed = client.warehouses.get(identity)
        samples.append({"at": now(), "state": observed.state.value})
        if observed.state.value == "STOPPED":
            break
        time.sleep(10)
    elapsed = time.monotonic() - start
    final_state = ControlStore().read()[0]
    independent = final_state["state"] in {"STARTING", "AWAKE"} and datetime.now(
        timezone.utc
    ) < instant(state["session"]["deadline_utc"])
    status = (
        "PASS"
        if samples[-1]["state"] == "STOPPED" and elapsed <= 360 and independent
        else "FAIL"
    )
    save(
        ROOT / "output/platform-foundation/warehouse-idle.json",
        {
            "status": status,
            "warehouse_id": identity,
            "last_statement_id": response.statement_id,
            "last_query_completed_at": last_query_completed.isoformat(),
            "stop_elapsed_seconds": round(elapsed, 3),
            "samples": samples,
            "poll_method": "warehouses.get only",
            "explicit_stop_in_probe": False,
            "concurrent_control_shutdown_excluded": independent,
        },
    )
    if status != "PASS":
        raise AssertionError("Warehouse did not automatically stop within six minutes")
    print(f"PASS: warehouse stopped after {elapsed:.1f}s")


if __name__ == "__main__":
    main()
