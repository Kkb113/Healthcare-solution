"""One funded Search lifecycle with three precomputed nonpatient vectors.

No embedding API/model or SQL warehouse is used. The full 24-hour tail remains
reserved even after both index and endpoint are confirmed deleted.
"""

import argparse
import json
import time
from datetime import datetime, timedelta, timezone

from databricks.sdk.errors import (
    BadRequest,
    NotFound,
    PermissionDenied,
    TemporarilyUnavailable,
    TooManyRequests,
)
from databricks.sdk.service.vectorsearch import (
    DirectAccessVectorIndexSpec,
    EmbeddingVectorColumn,
    EndpointType,
    VectorIndexType,
)
from foundation_support import ROOT, databricks_clients, load, now, save
from platform_control import ControlStore, admission, admit_operation, instant, register
from probe_security_baseline import VALIDATION, principal_client

ENDPOINT = "hcp-foundation-search"
INDEX = "hc_test._foundation_probe.hcp_foundation_search"
POLICY = "bc6afd45-e76f-3af8-89af-cca1fbf5b603"


def vector(position):
    return [float(i == position) for i in range(768)]


def wait_deleted(get, maximum_seconds):
    deadline = time.monotonic() + maximum_seconds
    while time.monotonic() < deadline:
        try:
            get()
        except NotFound:
            return True
        time.sleep(3)
    return False


def main():
    global ENDPOINT
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry-approved", action="store_true")
    args = parser.parse_args()
    if args.retry_approved:
        amendment = load(ROOT / "platform/config/probe-budget-revision.json")
        if amendment["status"] != "APPROVED":
            raise PermissionError("Retry funding not approved")
        ENDPOINT = "hcp-foundation-search-retry"
    store = ControlStore()
    state = store.read()[0]
    admission(state, True)
    if (
        instant(state["session"]["deadline_utc"]) - datetime.now(timezone.utc)
    ).total_seconds() < 1740:
        raise PermissionError("A fresh 30-minute guarded window is required")
    account, client = databricks_clients()
    # The lifecycle is single-use. Even an interrupted create consumes its full
    # reservation until provider reconciliation; rerunning must not create again.
    existing_cycles = sum(
        x["units"]
        for x in state.get("cost_claims", {}).values()
        if x.get("meter") == "search_cycles"
    )
    if existing_cycles != (1 if args.retry_approved else 0):
        raise PermissionError("Search lifecycle count must match approved attempt")
    admit_operation(
        store,
        "search-foundation-retry"
        if args.retry_approved
        else "search-foundation-lifecycle",
        "search_cycles",
        1,
    )
    store.transact(
        lambda value: register(
            value,
            {
                "kind": "search",
                "id": ENDPOINT,
                "name": ENDPOINT,
                "owner": "api-adapter",
            },
        )
    )
    report = {
        "status": "INCOMPLETE",
        "started_at": now(),
        "endpoint": ENDPOINT,
        "index": INDEX,
        "fixture_rows": 3,
        "embedding_dimensions": 768,
        "tail_reserved_hours": 24,
        "embedding_inference_calls": 0,
        "sql_queries": 0,
        "cleanup": {},
        "stages": [],
    }
    try:
        created = client.vector_search_endpoints.create_endpoint(
            ENDPOINT, EndpointType.STANDARD, usage_policy_id=POLICY
        ).result(timeout=timedelta(minutes=18))
        report["stages"].append(
            {"stage": "endpoint_online", "at": now(), "id": created.id}
        )
        client.vector_search_indexes.create_index(
            INDEX,
            ENDPOINT,
            "id",
            VectorIndexType.DIRECT_ACCESS,
            direct_access_index_spec=DirectAccessVectorIndexSpec(
                schema_json=json.dumps(
                    {"id": "string", "text": "string", "embedding": "array<float>"}
                ),
                embedding_vector_columns=[
                    EmbeddingVectorColumn(name="embedding", embedding_dimension=768)
                ],
            ),
        )
        deadline = min(
            time.monotonic() + 1200,
            time.monotonic()
            + (
                instant(state["session"]["deadline_utc"]) - datetime.now(timezone.utc)
            ).total_seconds()
            - 300,
        )
        inputs = json.dumps(
            [
                {
                    "id": str(i),
                    "text": f"Nonpatient constant document {i}",
                    "embedding": vector(i),
                }
                for i in range(3)
            ]
        )
        # Upserts are keyed by the same immutable IDs and vectors, so retrying a
        # documented initializing/transient response cannot duplicate rows.
        while True:
            try:
                upserted = client.vector_search_indexes.upsert_data_vector_index(
                    INDEX, inputs
                )
                report["upsert_response"] = upserted.as_dict()
                break
            except (BadRequest, TemporarilyUnavailable, TooManyRequests) as error:
                if isinstance(error, BadRequest) and not any(
                    word in str(error).lower()
                    for word in ["ready", "initializ", "provision", "creating"]
                ):
                    raise
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        "Index did not accept its fixed keyed upsert"
                    ) from error
                report["last_initializing_error"] = type(error).__name__
                save(ROOT / "output/platform-foundation/search-progress.json", report)
                time.sleep(10)
        samples = []
        while True:
            status = client.vector_search_indexes.get_index(INDEX).status
            samples.append({"at": now(), "status": status.as_dict() if status else {}})
            report["readiness_samples"] = samples
            save(ROOT / "output/platform-foundation/search-progress.json", report)
            if status and status.ready:
                result = client.vector_search_indexes.query_index(
                    INDEX, ["id", "text"], query_vector=vector(0), num_results=1
                )
                if (
                    result.result
                    and result.result.data_array
                    and result.result.data_array[0][0] == "0"
                ):
                    break
            if time.monotonic() >= deadline:
                raise AssertionError(
                    "Expected nearest vector did not reconcile within readiness allowance"
                )
            time.sleep(10)
        report["stages"].append(
            {"stage": "expected_nearest_hit", "at": now(), "id": "0"}
        )
        with principal_client(account, VALIDATION) as wrong:
            try:
                wrong.vector_search_indexes.query_index(
                    INDEX, ["id"], query_vector=vector(0), num_results=1
                )
            except (PermissionDenied, NotFound) as error:
                report["stages"].append(
                    {
                        "stage": "wrong_principal_denied",
                        "at": now(),
                        "type": type(error).__name__,
                        "positive_control": "same index already queried successfully by owner",
                    }
                )
            else:
                raise AssertionError(
                    "Validation caller unexpectedly queried search index"
                )
        report["status"] = "PASS"
    except Exception as error:  # noqa: BLE001 - bounded cloud probe, always cleanup
        report["failure"] = {
            "type": type(error).__name__,
            "code": getattr(error, "error_code", None),
        }
    finally:
        for label, delete, get in [
            (
                "index",
                lambda: client.vector_search_indexes.delete_index(INDEX),
                lambda: client.vector_search_indexes.get_index(INDEX),
            ),
            (
                "endpoint",
                lambda: client.vector_search_endpoints.delete_endpoint(ENDPOINT),
                lambda: client.vector_search_endpoints.get_endpoint(ENDPOINT),
            ),
        ]:
            try:
                try:
                    delete()
                except NotFound:
                    pass
                report["cleanup"][label] = wait_deleted(get, 150)
            except Exception as error:  # noqa: BLE001 - retain cleanup failure, continue to other owner
                report["cleanup"][label] = {"error_type": type(error).__name__}
        if any(report["cleanup"].get(key) is not True for key in ["index", "endpoint"]):
            report["status"] = "FAIL_CLEANUP"
        report["completed_at"] = now()
        save(ROOT / "output/platform-foundation/search-probe.json", report)
    print(json.dumps(report))
    if report["status"] != "PASS":
        raise RuntimeError("Search capability probe failed; see sanitized report")


if __name__ == "__main__":
    main()
