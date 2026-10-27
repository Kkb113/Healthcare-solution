"""Register existing Entra foundation principals and scope workspace access.

This adapter owns account/workspace identity registration only. Entra objects,
federated credentials and Azure roles are owned by foundation Terraform.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from databricks.sdk import AccountClient
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
        registered[name] = {
            **identity,
            "databricks_principal_id": principal.id,
            "workspace_permission": "USER",
        }
    public = {
        **foundation,
        "principals": registered,
        "workspace_id": config["workspace_id"],
        "oidc_subject": "repo:Kkb113/Healthcare-solution:ref:refs/heads/main",
        "cloud_data_grants": "none; phase-specific grants follow independent allow/deny tests",
    }
    (ROOT / "platform/config/foundation-resources.json").write_text(
        json.dumps(public, indent=2) + "\n"
    )
    print(json.dumps({"status": "PASS", "registered": registered}, indent=2))


if __name__ == "__main__":
    main()
