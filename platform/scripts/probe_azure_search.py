"""Two bounded Basic Search lifecycles; constant nonpatient fixtures only."""

import argparse
import hashlib
import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone

from azure_search_lifecycle import (
    RESOURCE_ID,
    SUBSCRIPTION,
    create_service,
    data_client,
    data_request,
    delete_service,
    documents,
    get_service,
    grant_operator,
    index_definition,
    scoped_query,
    vector,
    verify_hits,
    verify_service,
    wait_absent,
)
from foundation_support import ROOT, CloudHttpError, load, now, save
from platform_control import ControlStore, admission, instant

OUTPUT = ROOT / "output/platform-foundation/azure-search-probe.json"
INDEX = "indexes/hcp-foundation-documents"


@contextmanager
def denied_principal():
    """Existing HC managed identity, no Search grants and no new app secrets."""
    from databricks.sdk.service.catalog import (
        GenerateTemporaryServiceCredentialAzureOptions,
    )
    from platform_control import workspace_client

    credential = workspace_client().credentials.generate_temporary_service_credential(
        "hcp_luna_gateway",
        azure_options=GenerateTemporaryServiceCredentialAzureOptions(
            resources=["https://search.azure.com/.default"]
        ),
    )
    if not credential.azure_aad or not credential.azure_aad.aad_token:
        raise PermissionError("No authenticated managed-identity credential")
    wrong = data_client()
    wrong._token = credential.azure_aad.aad_token
    try:
        yield wrong
    finally:
        wrong._token = None
        credential.azure_aad.aad_token = None


def eventually(action, deadline, allowed=(401, 403, 404, 409, 429, 503)):
    while True:
        try:
            return action()
        except CloudHttpError as error:
            if error.status not in allowed or time.monotonic() >= deadline:
                raise
            time.sleep(5)


def rebuild(store, operation, report):
    if (
        instant(store.read()[0]["session"]["deadline_utc"]) - datetime.now(timezone.utc)
    ).total_seconds() < 900:
        raise PermissionError(
            "Search needs fifteen minutes plus independent guarded cleanup"
        )
    started = time.monotonic()
    create_service(store, operation)
    deadline = started + 660
    while True:
        service = get_service()
        if service:
            verify_service(service)
            if service["properties"]["provisioningState"].lower() == "succeeded":
                break
            if service["properties"]["provisioningState"].lower() == "failed":
                raise RuntimeError("Azure Search provisioning failed")
        if time.monotonic() >= deadline:
            raise TimeoutError("Azure Search not ready within funded window")
        admission(store.read()[0], True)
        time.sleep(5)
    grant_operator()
    data = data_client()
    eventually(lambda: data_request(data, "PUT", INDEX, index_definition()), deadline)
    items = [{"@search.action": "mergeOrUpload", **d} for d in documents()]
    result = eventually(
        lambda: data_request(data, "POST", INDEX + "/docs/index", {"value": items}),
        deadline,
    )
    if len(result["value"]) != 3 or not all(x["status"] for x in result["value"]):
        raise AssertionError("Index upload did not acknowledge every document")
    while True:
        result = data_request(
            data,
            "POST",
            INDEX + "/docs/search",
            scoped_query(["A"], ["OPERATIONAL"], vector(0)),
        )
        hits = verify_hits(result["value"], ["A"], ["OPERATIONAL"])
        if hits and hits[0]["id"] == "0" and {x["id"] for x in hits} == {"0", "2"}:
            break
        if time.monotonic() >= deadline:
            raise TimeoutError("Expected scoped documents not searchable")
        time.sleep(3)
    other = data_request(
        data,
        "POST",
        INDEX + "/docs/search",
        scoped_query(["B"], ["OPERATIONAL"], vector(1)),
    )
    assert [x["id"] for x in verify_hits(other["value"], ["B"], ["OPERATIONAL"])] == [
        "1"
    ]
    canonical = json.dumps(
        [
            {
                k: h[k]
                for k in [
                    "id",
                    "text",
                    "facility_id",
                    "security_class",
                    "document_version",
                ]
            }
            for h in hits
        ],
        sort_keys=True,
    ).encode()
    report["lifecycles"].append(
        {
            "operation": operation,
            "ready_at": now(),
            "elapsed_to_ready_seconds": round(time.monotonic() - started, 3),
            "expected_hit": "0",
            "scoped_ids_A": [h["id"] for h in hits],
            "scoped_ids_B": ["1"],
            "authorized_result_sha256": hashlib.sha256(canonical).hexdigest(),
            "local_auth_disabled": True,
            "source_document_count": 3,
        }
    )
    save(OUTPUT, report)
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume-rejected-request", action="store_true")
    parser.add_argument("--complete-retained-lifecycle", action="store_true")
    args = parser.parse_args()
    prior_lifecycle = None
    if OUTPUT.exists():
        prior = load(OUTPUT)
        if args.complete_retained_lifecycle:
            if not (
                len(prior["lifecycles"]) == 1
                and prior.get("failure", {}).get("type") == "InvalidURL"
                and prior["cleanup"].get("service_deleted") is True
                and get_service() is None
            ):
                raise PermissionError(
                    "Only the proven first lifecycle may be reconciled"
                )
            retained = OUTPUT.with_name("azure-search-first-lifecycle.json")
            if retained.exists():
                raise PermissionError("First lifecycle already resumed")
            save(retained, prior)
            prior_lifecycle = prior
        elif not (
            args.resume_rejected_request
            and prior.get("failure", {}).get("code") == "BadRequest"
            and not prior["lifecycles"]
            and prior["cleanup"].get("service_deleted") is True
            and get_service() is None
        ):
            raise PermissionError(
                "Reconcile the retained Search attempt before another paid lifecycle"
            )
        if args.resume_rejected_request:
            retained = OUTPUT.with_name("azure-search-rejected-request.json")
            if retained.exists():
                raise PermissionError(
                    "The explicitly rejected request has already been resumed"
                )
            save(retained, prior)
    store = ControlStore()
    admission(store.read()[0], True)
    report = {
        "status": "INCOMPLETE",
        "started_at": now(),
        "backend": "azure-ai-search-basic",
        "subscription_id": SUBSCRIPTION,
        "resource_id": RESOURCE_ID,
        "lifecycles": [],
        "cleanup": {},
        "embedding_model_calls": 0,
        "sql_queries": 0,
        "source_fixture_sha256": hashlib.sha256(
            json.dumps(documents(), sort_keys=True).encode()
        ).hexdigest(),
    }
    if prior_lifecycle:
        report["lifecycles"] = prior_lifecycle["lifecycles"]
        report["first_service_deleted"] = True
        report["retained_harness_failure"] = {
            "path": "output/platform-foundation/azure-search-first-lifecycle.json",
            "status": "FAIL",
            "type": "InvalidURL",
            "disposition": "First service was functional and deleted; corrected credential lookup is tested during the second reserved lifecycle",
        }
    save(OUTPUT, report)
    try:
        data = rebuild(
            store,
            "azure-search-rebuild-lifecycle"
            if prior_lifecycle
            else "azure-search-first-lifecycle",
            report,
        )
        with denied_principal() as wrong:
            try:
                data_request(
                    wrong,
                    "POST",
                    INDEX + "/docs/search",
                    scoped_query(["A"], ["OPERATIONAL"], vector(0)),
                )
            except CloudHttpError as error:
                if error.status != 403:
                    raise
                report["wrong_entra_principal_denied"] = True
                report["denial_http_status"] = 403
            else:
                raise AssertionError("Ungranted principal read the search index")
        report["negative_probe_credential_process_local_cleared"] = True
        report["new_application_secrets_created"] = 0
        # Exercise native delete/reinsert propagation, using a different facility.
        deleted = data_request(
            data,
            "POST",
            INDEX + "/docs/index",
            {"value": [{"@search.action": "delete", "id": "1"}]},
        )
        assert deleted["value"][0]["status"]
        limit = time.monotonic() + 90
        while True:
            hits = data_request(
                data,
                "POST",
                INDEX + "/docs/search",
                scoped_query(["B"], ["OPERATIONAL"], vector(1)),
            )["value"]
            if not hits:
                break
            if time.monotonic() >= limit:
                raise TimeoutError("Index delete did not propagate")
            time.sleep(3)
        report["document_deletion_propagated"] = True
        if not prior_lifecycle:
            delete_service()
            wait_absent()
            report["first_service_deleted"] = True
            rebuild(store, "azure-search-rebuild-lifecycle", report)
        assert (
            report["lifecycles"][0]["authorized_result_sha256"]
            == report["lifecycles"][1]["authorized_result_sha256"]
        )
        report["rebuild_integrity"] = True
        report["status"] = "PASS"
    except Exception as error:
        report["status"] = "FAIL"
        report["failure"] = {
            "type": type(error).__name__,
            "code": getattr(error, "code", None),
            "message": str(error)[:250]
            if not isinstance(error, CloudHttpError)
            else str(error),
        }
        raise
    finally:
        try:
            delete_service()
            wait_absent()
            report["cleanup"]["service_deleted"] = True
        except Exception as error:  # noqa: BLE001 -- finish cleanup and retain its failure
            report["status"] = "CLEANUP_FAILED"
            report["cleanup"]["error_type"] = type(error).__name__
        report["completed_at"] = now()
        save(OUTPUT, report)
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "lifecycles": len(report["lifecycles"]),
                    "cleanup": report["cleanup"],
                }
            )
        )


if __name__ == "__main__":
    main()
