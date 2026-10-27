"""Control-plane-only Lakebase inspection and hard disable for owned fixtures."""

from datetime import timedelta

from databricks.sdk.common.lro import LroOptions
from databricks.sdk.errors import NotFound
from databricks.sdk.service import postgres as pg

PROJECT = "projects/hcp-foundation-lakebase"
SYNC = "synced_tables/hc_test._foundation_probe.hcp_synced_fixture"


def verify_sync_project(synced):
    # GA GetSyncedTable can omit spec and return status.project only. A known
    # resource name is insufficient on its own; require an explicit project
    # attestation and reject conflicting/missing identity before any mutation.
    spec = getattr(synced, "spec", None)
    status = getattr(synced, "status", None)
    branch = getattr(spec, "branch", None)
    declared = branch.split("/branches/")[0] if branch else None
    observed = getattr(status, "project", None)
    projects = {value for value in [declared, observed] if value}
    if projects != {PROJECT}:
        raise PermissionError(
            "Synced table has missing or conflicting project identity"
        )


def scoped_endpoint(name):
    parts = name.split("/")
    if (
        len(parts) != 6
        or "/".join(parts[:2]) != PROJECT
        or parts[2] != "branches"
        or parts[4] != "endpoints"
    ):
        raise PermissionError(
            "Lakebase endpoint is outside the temporary fixture project"
        )
    return name


def inspect_resources(client, registered):
    records = []
    pipelines = set()
    projects = {r["id"] for r in registered if r["kind"] == "lakebase"}
    syncs = {r["id"] for r in registered if r["kind"] == "synced_table"}
    if syncs - {SYNC}:
        raise PermissionError("No safe temporary synced-table lifecycle contract")
    if syncs:
        projects.add(PROJECT)
    if projects - {PROJECT}:
        raise PermissionError("No lifecycle adapter exists for this Lakebase project")
    live_project = False
    disabled_project = False
    for name in projects:
        try:
            project = client.postgres.get_project(name)
        except NotFound:
            continue
        live_project = True
        endpoint_disabled = []
        for branch in client.postgres.list_branches(project.name):
            for endpoint in client.postgres.list_endpoints(branch.name):
                scoped_endpoint(endpoint.name)
                disabled = endpoint.status and endpoint.status.disabled is True
                endpoint_disabled.append(bool(disabled))
                records.append(
                    {
                        "kind": "lakebase",
                        "id": endpoint.name,
                        "name": "hcp-foundation-lakebase",
                        "owner": "api-adapter",
                        "owned": True,
                        "running": not disabled,
                        "state": endpoint.status.current_state.value
                        if endpoint.status and endpoint.status.current_state
                        else "UNKNOWN",
                        "hard_disabled": bool(disabled),
                    }
                )
        disabled_project = bool(endpoint_disabled) and all(endpoint_disabled)
    if syncs:
        # GetSyncedTable is NOT safe for sleep inspection: this tenant's GA
        # implementation tries to connect to Postgres and rejects a disabled
        # endpoint. Only Jobs/Pipelines and project/endpoint metadata are read.
        # Discover the exact fixture's internally generated pipeline by its
        # closed source name plus catalog/schema/run-as identity.
        prefix = "Synced table: hc_test._foundation_probe.hcp_synced_fixture "
        for candidate in client.pipelines.list_pipelines():
            if not candidate.name.startswith(prefix):
                continue
            detail = client.pipelines.get(candidate.pipeline_id)
            if (
                not detail.spec
                or detail.spec.catalog != "hc_test"
                or detail.spec.schema != "_foundation_probe"
                or detail.run_as_user_name != "658faa8a-72bf-4285-bf4c-3cd25778ac5f"
            ):
                raise PermissionError("Sync pipeline scope/identity mismatch")
            pipelines.add(candidate.pipeline_id)
        records.append(
            {
                "kind": "synced_table",
                "id": SYNC,
                "name": "hcp-foundation-synced",
                "owner": "api-adapter",
                "owned": True,
                "running": live_project and not disabled_project,
                "state": "PROJECT_HARD_DISABLED"
                if disabled_project
                else "REGISTERED_METADATA_NOT_QUERIED",
            }
        )
    return records, pipelines


def hard_disable(client, endpoint):
    scoped_endpoint(endpoint)
    operation = client.postgres.update_endpoint(
        endpoint,
        pg.Endpoint(
            name=endpoint,
            spec=pg.EndpointSpec(
                endpoint_type=pg.EndpointType.ENDPOINT_TYPE_READ_WRITE,
                disabled=True,
            ),
        ),
        pg.FieldMask(["spec.disabled"]),
    )
    operation.wait(LroOptions(timeout=timedelta(seconds=90)))
    if client.postgres.get_endpoint(endpoint).status.disabled is not True:
        raise AssertionError("Lakebase hard-disable readback failed")


def remove_temporary_sync(client, name):
    if name != SYNC:
        raise PermissionError("Only the constant fixture synced copy may be deleted")
    client.postgres.delete_synced_table(name).wait(
        LroOptions(timeout=timedelta(seconds=90))
    )
