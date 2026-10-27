"""CI deployment admission: exact target, pinned workspace, funded window, safe ACL.

Deploys metadata only. Executing smoke runs is a separately reserved operation.
No production deployment and no implicit waking on merge.
"""

import os
import subprocess

from foundation_ledger import BlobLedger, exposure
from foundation_support import ROOT, now, save
from platform_control import ControlStore, admission, workspace_client


def main():
    target = os.environ.get("HCP_SELECTED_TARGET")
    if target not in {"dev", "test"} or os.environ.get("HCP_FUNDED_WINDOW") != "true":
        raise PermissionError("Explicit funded dev/test target required")
    state = ControlStore().read()[0]
    ledger = BlobLedger().read()[0]
    admission(
        state,
        state["session"]["reservation_id"] in ledger["reservations"]
        and not exposure(ledger)["pause_new_work"],
    )
    client = workspace_client()
    folder = client.workspace.get_status("/hcp")
    permissions = client.permissions.get("directories", str(folder.object_id))
    for rule in permissions.access_control_list:
        if rule.group_name == "users" and any(
            p.permission_level.value in {"CAN_EDIT", "CAN_MANAGE"}
            for p in rule.all_permissions
        ):
            raise PermissionError("Untrusted workspace users can edit bundle artifacts")
    subprocess.run(
        ["databricks", "bundle", "deploy", "--target", target, "--auto-approve"],
        cwd=ROOT / "platform",
        check=True,
        timeout=600,
    )
    save(
        ROOT / "output/platform-foundation/bundle-deployment.json",
        {
            "status": "PASS",
            "target": target,
            "source_sha": os.environ.get("GITHUB_SHA"),
            "observed_at": now(),
            "session_id": state["session"]["id"],
            "workloads_launched": 0,
            "cost_estimate_paise": 0,
            "tests": "same locked Linux suite before deployment; smoke execution separately funded",
        },
    )


if __name__ == "__main__":
    main()
