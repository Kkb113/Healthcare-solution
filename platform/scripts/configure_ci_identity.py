"""Register existing Entra foundation principals and scope workspace access.

This adapter owns account/workspace identity registration only. Entra objects,
federated credentials and Azure roles are owned by foundation Terraform.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from databricks.sdk import AccountClient, WorkspaceClient
from databricks.sdk.service import iam

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    config = json.loads((ROOT / "platform/config/workspace.json").read_text())
    foundation = json.loads(
        (ROOT / "output/platform-readiness/foundation-resources.json").read_text(
            encoding="utf-8-sig"
        )
    )
    os.environ["ARM_SUBSCRIPTION_ID"] = config["subscription_id"]
    account = AccountClient(profile=config["account_profile"])
    workspace = WorkspaceClient(profile=config["workspace_profile"])
    registered = {}
    for name, identity in foundation["principals"].items():
        matches = list(
            account.service_principals.list(
                filter=f'applicationId eq "{identity["client_id"]}"'
            )
        )
        if len(matches) > 1:
            raise ValueError(f"Ambiguous account identity: {name}")
        principal = (
            matches[0]
            if matches
            else account.service_principals.create(
                application_id=identity["client_id"],
                display_name=name,
                external_id=identity["object_id"],
                active=True,
            )
        )
        account.workspace_assignment.update(
            workspace_id=config["workspace_id"],
            principal_id=int(principal.id),
            permissions=[iam.WorkspacePermission.USER],
        )
        current = workspace.service_principals.get(principal.id)
        required_entitlements = ["workspace-access"]
        if name == "sp-hcp-cicd":
            # SQL service access permits warehouse API checks. It does not grant
            # warehouse CAN_USE, business-table access or administrator roles.
            required_entitlements.append("databricks-sql-access")
        missing = sorted(
            set(required_entitlements)
            - {entry.value for entry in current.entitlements or []}
        )
        if missing:
            workspace.service_principals.patch(
                principal.id,
                schemas=[
                    iam.PatchSchema.URN_IETF_PARAMS_SCIM_API_MESSAGES_2_0_PATCH_OP
                ],
                operations=[
                    iam.Patch(
                        op=iam.PatchOp.ADD,
                        path="entitlements",
                        value=[{"value": value} for value in missing],
                    )
                ],
            )
        registered[name] = {
            **identity,
            "databricks_principal_id": principal.id,
            "workspace_permission": "USER",
            "entitlements": required_entitlements,
        }
    public = {
        **foundation,
        "principals": registered,
        "workspace_id": config["workspace_id"],
        "oidc_subject": foundation["oidc_subject"],
        "cloud_data_grants": "none; phase-specific grants follow independent allow/deny tests",
    }
    (ROOT / "platform/config/foundation-resources.json").write_text(
        json.dumps(public, indent=2) + "\n"
    )
    print(json.dumps({"status": "PASS", "registered": registered}, indent=2))


if __name__ == "__main__":
    main()
