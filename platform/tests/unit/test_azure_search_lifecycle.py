import copy
import json

import pytest
from azure_search_lifecycle import (
    RESOURCE_ID,
    delete_service,
    documents,
    index_definition,
    inspect_resources,
    resource_url,
    scoped_query,
    vector,
    verify_hits,
    verify_service,
)
from collect_probe_billing import billing_query
from foundation_support import CloudHttpError


def service():
    return {
        "id": RESOURCE_ID,
        "location": "eastus",
        "sku": {"name": "basic"},
        "tags": {"project": "healthcare-platform", "lifecycle-owner": "hcp-control"},
        "properties": {
            "disableLocalAuth": True,
            "replicaCount": 1,
            "partitionCount": 1,
            "provisioningState": "Succeeded",
        },
    }


@pytest.mark.parametrize("scope", [[], ["A' or true"], ["other"]])
def test_untrusted_or_missing_scope_is_rejected_before_network(scope):
    with pytest.raises(PermissionError):
        scoped_query(scope, ["OPERATIONAL"], vector(0))


def test_filters_precede_retrieval_and_each_hit_is_rechecked():
    body = scoped_query(["A"], ["OPERATIONAL"], vector(0))
    assert (
        body["vectorFilterMode"] == "preFilter"
        and "facility_id eq 'A'" in body["filter"]
    )
    with pytest.raises(PermissionError):
        verify_hits([documents()[1]], ["A"], ["OPERATIONAL"])
    missing_version = documents()[0] | {"document_version": None}
    with pytest.raises(PermissionError):
        verify_hits([missing_version], ["A"], ["OPERATIONAL"])
    with pytest.raises(ValueError):
        scoped_query(["A"], ["OPERATIONAL"], [1.0])
    assert index_definition()["fields"][-1]["retrievable"] is False


@pytest.mark.parametrize(
    "edit",
    [
        lambda x: x["sku"].update(name="standard"),
        lambda x: x["properties"].update(replicaCount=2),
        lambda x: x["properties"].update(disableLocalAuth=False),
        lambda x: x["tags"].update(project="other"),
    ],
)
def test_cost_or_ownership_drift_prevents_deletion(edit):
    value = copy.deepcopy(service())
    edit(value)
    with pytest.raises(PermissionError):
        verify_service(value)


def test_inspection_is_metadata_only_and_any_existing_basic_service_is_billable():
    class Fixture:
        def request(self, method, url):
            assert method == "GET" and url == resource_url()
            return 200, {}, json.dumps(service()).encode()

    row = inspect_resources(Fixture())[0]
    assert row["running"] and row["kind"] == "azure_search"
    with pytest.raises(ValueError):
        delete_service(RESOURCE_ID + "-other", Fixture())


def test_contributor_guard_deletes_capacity_when_role_revocation_is_denied():
    calls = []

    class Fixture:
        def request(self, method, url):
            calls.append((method, url))
            if "/roleAssignments/" in url:
                raise CloudHttpError(403, "AuthorizationFailed")
            return 200, {}, json.dumps(service()).encode()

    assert delete_service(client=Fixture())["pending_role_cleanup"] == 2
    assert calls[-1] == ("DELETE", resource_url())


def test_billing_retains_product_caller_corrections_prices_and_closed_project_scope():
    query = billing_query()
    assert "billing_origin_product" in query and "identity_metadata" in query
    assert "RETRACTION" in query and "SUM(u.usage_quantity)" in query
    assert (
        "u.workspace_id IS NULL" in query
        and "14fc3c6c-8800-4de9-a5e1-5e9d2a1fb3a5" in query
    )
    assert (
        "u.usage_unit = p.usage_unit" in query
        and "u.usage_start_time < p.price_end_time" in query
    )
