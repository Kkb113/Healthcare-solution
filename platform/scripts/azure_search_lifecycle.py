"""Healthcare-only, keyless Azure Basic Search lifecycle. No implicit creates.

Metadata inspection never queries an index. The external guard can delete the
fixed service even if its control manifest is unavailable. Source documents and
embeddings live outside this disposable service; recreation restores ACLs first.
"""

from __future__ import annotations

import json
import time
import uuid

from foundation_support import ROOT, AzureRest, CloudHttpError, load

CONFIG = ROOT / "platform/config/search-backend.json"
SUBSCRIPTION = "d054aa64-95db-467b-a25c-387de70b15bd"
RESOURCE_ID = f"/subscriptions/{SUBSCRIPTION}/resourceGroups/rg-hcp-dev/providers/Microsoft.Search/searchServices/hcp-search-d054-dev"
OPERATOR = "5ee77c8e-621d-4953-9502-1be929c977e1"
ROLES = {
    "7ca78c08-252a-4471-8644-bb5ff32d4ba0": OPERATOR,
    "8ebe5a00-799e-43f5-93ac-243d3dce84a7": OPERATOR,
}


def arm():
    return AzureRest(
        SUBSCRIPTION, "https://management.azure.com/", {"management.azure.com"}
    )


def resource_url(identity=RESOURCE_ID):
    if identity != RESOURCE_ID:
        raise ValueError("Search resource escaped the fixed healthcare scope")
    return f"https://management.azure.com{identity}?api-version={load(CONFIG)['management_api']}"


def get_service(client=None):
    try:
        _, _, raw = (client or arm()).request("GET", resource_url())
        return json.loads(raw)
    except CloudHttpError as error:
        if error.status == 404:
            return None
        raise


def verify_service(service):
    p = service["properties"]
    if (
        service["id"].lower() != RESOURCE_ID.lower()
        or service["location"].lower().replace(" ", "") != "eastus"
        or service["sku"]["name"].lower() != "basic"
        or p["replicaCount"] != 1
        or p["partitionCount"] != 1
        or not p.get("disableLocalAuth")
        or service.get("tags", {}).get("project") != "healthcare-platform"
        or service.get("tags", {}).get("lifecycle-owner") != "hcp-control"
    ):
        raise PermissionError(
            "Search identity, cost, authentication or ownership drift"
        )


def inspect_resources(client=None):
    service = get_service(client)
    if service is None:
        return []
    verify_service(service)
    return [
        {
            "kind": "azure_search",
            "id": RESOURCE_ID,
            "name": "hcp-search-d054-dev",
            "owner": "api-adapter",
            "owned": True,
            "running": True,
            "state": service["properties"].get("provisioningState", "UNKNOWN"),
        }
    ]


def role_url(role, principal):
    identity = uuid.uuid5(uuid.NAMESPACE_URL, f"{RESOURCE_ID}/{principal}/{role}")
    return f"https://management.azure.com{RESOURCE_ID}/providers/Microsoft.Authorization/roleAssignments/{identity}?api-version=2022-04-01"


def delete_service(identity=RESOURCE_ID, client=None):
    resource_url(identity)
    client = client or arm()
    service = get_service(client)
    if service is None:
        return
    verify_service(service)
    pending_roles = []
    for role, principal in ROLES.items():
        url = role_url(role, principal)
        try:
            _, _, raw = client.request("GET", url)
            actual = json.loads(raw)["properties"]
            if (
                actual["principalId"] != principal
                or actual["scope"].lower() != RESOURCE_ID.lower()
            ):
                raise PermissionError("Unexpected role assignment; refusing deletion")
            client.request("DELETE", url)
        except CloudHttpError as error:
            if error.status == 403:
                # A Contributor guard can delete the service but cannot revoke
                # RBAC. Do not leave billable capacity up while cleaning roles.
                pending_roles.append((role, principal))
            elif error.status != 404:
                raise
    client.request("DELETE", resource_url())
    return {"pending_role_cleanup": len(pending_roles)}


def create_service(store, operation_id, client=None):
    from platform_control import admit_operation, register

    client = client or arm()
    if get_service(client) is not None:
        raise PermissionError(
            "Reconcile existing Search service before a new lifecycle"
        )
    # Reserve and register before PUT. Timeout does not refund an uncertain create.
    admit_operation(store, operation_id, "azure_search_hours", 1)
    store.transact(
        lambda value: register(
            value,
            {
                "kind": "azure_search",
                "id": RESOURCE_ID,
                "name": "hcp-search-d054-dev",
                "owner": "api-adapter",
            },
        )
    )
    from platform_control import admission

    admission(store.read()[0], True)
    client.request(
        "PUT",
        resource_url(),
        body={
            "location": "eastus",
            "sku": {"name": "basic"},
            "tags": {
                "project": "healthcare-platform",
                "environment": "dev",
                "lifecycle-owner": "hcp-control",
            },
            "properties": {
                "replicaCount": 1,
                "partitionCount": 1,
                "hostingMode": "default",
                "disableLocalAuth": True,
                "publicNetworkAccess": "enabled",
            },
        },
    )


def grant_operator(client=None):
    client = client or arm()
    for role, principal in ROLES.items():
        client.request(
            "PUT",
            role_url(role, principal),
            body={
                "properties": {
                    "roleDefinitionId": f"/subscriptions/{SUBSCRIPTION}/providers/Microsoft.Authorization/roleDefinitions/{role}",
                    "principalId": principal,
                    "principalType": "User",
                }
            },
        )


def wait_absent(seconds=300):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if not inspect_resources():
            return
        time.sleep(5)
    raise TimeoutError("Search deletion not confirmed; cannot certify sleep")


def data_client():
    return AzureRest(
        SUBSCRIPTION,
        "https://search.azure.com/",
        {"hcp-search-d054-dev.search.windows.net"},
    )


def data_request(client, method, path, body=None):
    _, _, raw = client.request(
        method,
        f"https://hcp-search-d054-dev.search.windows.net/{path}?api-version={load(CONFIG)['data_api']}",
        body=body,
    )
    return json.loads(raw) if raw else None


def vector(position):
    return [float(i == position) for i in range(768)]


def documents():
    return [
        {
            "id": str(i),
            "text": f"Nonpatient constant document {i}",
            "facility_id": "A" if i != 1 else "B",
            "security_class": "OPERATIONAL",
            "document_version": "fixture-1",
            "embedding": vector(i),
        }
        for i in range(3)
    ]


def index_definition():
    fields = [
        {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
        {"name": "text", "type": "Edm.String", "searchable": True},
    ]
    fields += [
        {"name": name, "type": "Edm.String", "filterable": True}
        for name in ["facility_id", "security_class", "document_version"]
    ]
    fields += [
        {
            "name": "embedding",
            "type": "Collection(Edm.Single)",
            "searchable": True,
            "retrievable": False,
            "dimensions": 768,
            "vectorSearchProfile": "hcp-vector",
        }
    ]
    return {
        "name": load(CONFIG)["index_name"],
        "fields": fields,
        "vectorSearch": {
            "algorithms": [
                {
                    "name": "hcp-hnsw",
                    "kind": "hnsw",
                    "hnswParameters": {"metric": "cosine"},
                }
            ],
            "profiles": [{"name": "hcp-vector", "algorithm": "hcp-hnsw"}],
        },
    }


def scoped_query(facilities, security_classes, query_vector):
    # The application supplies verified entitlements, never caller-authored OData.
    if (
        not facilities
        or not security_classes
        or not set(facilities) <= {"A", "B"}
        or not set(security_classes) <= {"OPERATIONAL", "CLINICAL"}
    ):
        raise PermissionError("Missing or invalid verified retrieval scope")
    if len(query_vector) != 768:
        raise ValueError("Embedding dimension mismatch")
    facilities_filter = " or ".join(
        f"facility_id eq '{f}'" for f in sorted(set(facilities))
    )
    classes_filter = " or ".join(
        f"security_class eq '{c}'" for c in sorted(set(security_classes))
    )
    return {
        "vectorQueries": [
            {"kind": "vector", "vector": query_vector, "fields": "embedding", "k": 3}
        ],
        "filter": f"({facilities_filter}) and ({classes_filter})",
        "vectorFilterMode": "preFilter",
        "select": "id,text,facility_id,security_class,document_version",
        "top": 3,
    }


def verify_hits(hits, facilities, security_classes):
    for hit in hits:
        if (
            hit["facility_id"] not in facilities
            or hit["security_class"] not in security_classes
            or not hit.get("document_version")
        ):
            raise PermissionError("Unauthorized or unversioned retrieval hit")
    return hits
