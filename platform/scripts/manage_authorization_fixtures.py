"""Temporary Entra-backed service principals for eight actual healthcare roles.

No human user is created/changed, no Azure/Graph permission or Entra group
membership is granted. Databricks group membership is applied only by the test
runner while the dedicated healthcare connector is paused, then removed.
"""

import argparse
import json

from configure_foundation_identity import graph, request
from databricks.sdk.service.iam import ComplexValue, WorkspacePermission
from foundation_support import ROOT, databricks_clients, load, now, save

MANIFEST = ROOT / "output/platform-foundation/authorization-identities.json"
ROLES = [
    "platform-admins",
    "data-engineers",
    "data-scientists",
    "analysts",
    "clinical",
    "finance",
    "operations",
    "auditors",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "cleanup"])
    args = parser.parse_args()
    azure = graph()
    account, workspace = databricks_clients()
    manifest = (
        load(MANIFEST) if MANIFEST.exists() else {"started_at": now(), "principals": {}}
    )
    if args.action == "prepare":
        for role in ROLES:
            if role in manifest["principals"]:
                raise PermissionError(
                    "Prior fixture exists; reconcile before creating another identity"
                )
            name = "hcp-foundation-role-" + role
            application = request(
                azure,
                "POST",
                "applications",
                {
                    "displayName": name,
                    "signInAudience": "AzureADMyOrg",
                    "requiredResourceAccess": [],
                },
            )
            record = {
                "display_name": name,
                "application_object_id": application["id"],
                "application_id": application["appId"],
                "role": "hcp-" + role,
            }
            manifest["principals"][role] = record
            save(MANIFEST, manifest)
            principal = request(
                azure,
                "POST",
                "servicePrincipals",
                {"appId": application["appId"], "accountEnabled": True},
            )
            record["entra_object_id"] = principal["id"]
            save(MANIFEST, manifest)
            created = account.service_principals.create(
                application_id=application["appId"],
                external_id=principal["id"],
                display_name=name,
                active=True,
            )
            record["databricks_id"] = created.id
            save(MANIFEST, manifest)
            account.workspace_assignment.update(
                7405619366453187,
                int(created.id),
                permissions=[WorkspacePermission.USER],
            )
            workspace.service_principals.update(
                created.id,
                application_id=created.application_id,
                display_name=name,
                entitlements=[
                    ComplexValue(value="workspace-access"),
                    ComplexValue(value="databricks-sql-access"),
                ],
            )
            current = request(
                azure,
                "GET",
                f"servicePrincipals/{principal['id']}?$select=id,appId,displayName",
            )
            assert (
                current["id"] == record["entra_object_id"]
                and current["appId"] == record["application_id"]
            )
        manifest["status"] = "PREPARED_NO_GROUP_MEMBERSHIP_NO_SECRETS"
    else:
        for role, record in manifest["principals"].items():
            if (
                role not in ROLES
                or record["display_name"] != "hcp-foundation-role-" + role
            ):
                raise PermissionError("Fixture namespace mismatch")
            application = request(
                azure,
                "GET",
                f"applications/{record['application_object_id']}?$select=id,appId,displayName",
            )
            assert (
                application["displayName"] == record["display_name"]
                and application["appId"] == record["application_id"]
            )
            if record.get("databricks_id"):
                actual = account.service_principals.get(record["databricks_id"])
                assert (
                    actual.application_id == record["application_id"]
                    and actual.display_name == record["display_name"]
                )
                if actual.groups:
                    raise PermissionError(
                        "Remove temporary test group memberships before identity cleanup"
                    )
                for secret in account.service_principal_secrets.list(
                    record["databricks_id"]
                ):
                    account.service_principal_secrets.delete(
                        record["databricks_id"], secret.id
                    )
                account.workspace_assignment.delete(
                    7405619366453187, int(record["databricks_id"])
                )
                account.service_principals.delete(record["databricks_id"])
            if record.get("entra_object_id"):
                request(
                    azure, "DELETE", f"servicePrincipals/{record['entra_object_id']}"
                )
            request(azure, "DELETE", f"applications/{record['application_object_id']}")
            record["deleted_at"] = now()
            save(MANIFEST, manifest)
        manifest["status"] = "CLEANED_UP"
    manifest["updated_at"] = now()
    save(MANIFEST, manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "count": len(manifest["principals"]),
                "human_user_changes": 0,
                "azure_permissions_added": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
